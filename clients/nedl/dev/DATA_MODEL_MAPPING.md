# NËDL Data Model - Design & Findings

**Purpose:** Document validated relationships and key findings for entity resolution data model

**Last Updated:** 2025-12-22

---

## Target Model Overview

We're building a **dimensional model** with slowly changing dimensions (SCD Type 2) for entity resolution and ownership tracking.

```
dim_property (SCD Type 2)
  ↓
fact_transaction
  ↓ (via bridge tables)
dim_entity (SCD Type 2) ← dim_entity_identifier (many aliases)
```

### Core Tables

1. **dim_property** - Property master with historical snapshots
2. **dim_entity** - Canonical entities (owners, companies) with history
3. **dim_entity_identifier** - All aliases/names that map to entities (many-to-one)
4. **fact_transaction** - Transaction events (immutable)
5. **bridge_transaction_party** - Links transactions to multiple buyers/sellers
6. **bridge_property_owner** - Links properties to multiple owners over time

### Data Sources

1. **Cherre** (GraphQL API) - Primary data source
2. **Yardi** (Flat files) - Property names, additional attributes (90% coverage via address matching)
3. **NMHC** (Flat file) - Membership directory for entity enrichment

### Key Context from Engineering Team

**From Brett:**
> "cherre_transactions has 100% coverage - the root for the graphql query that populated every cherre table was tax_assessor id. Yardi was more of a challenge, I ended up with 90% coverage by using the cherre address standardization feature"

**Takeaways:**
- Processed `cherre_transactions` table (in Supabase) has 100% tax_assessor_id coverage
- Raw `recorder_v2` only has 70% coverage
- Team is working with processed tables, not raw GraphQL data directly

---

## Validated Cardinality (10k sample, 2025-12-22)

### Transaction → Party: MANY-TO-MANY ⚠️

**GRANTORS (Sellers):**
- 69.7% have exactly 1 grantor
- **30.1% have 2+ grantors** (joint sellers, married couples, partnerships)
- 0.2% have 0 grantors (mortgages, liens)

**GRANTEES (Buyers):**
- 56.7% have exactly 1 grantee
- **43.3% have 2+ grantees** (joint buyers, co-purchasers)

**Examples:**
- "CRYSTAL BIGELOW" + "NICHOLAS D BIGELOW" (married couple)
- "RICHARD E DINNEEN" + "THE RICHARD E DINNEEN TRUST" (person + trust)

**Model Requirement:** Bridge table `bridge_transaction_party` to avoid losing 30-43% of parties

---

### Property → Owner: ONE-TO-MANY

**Distribution:**
- 32.8% have exactly 1 owner
- **66.4% have 2+ simultaneous owners**
- 0.8% have 0 owners

**Analysis:** Multiple owners share same `last_seen_date` → **SIMULTANEOUS ownership** (joint tenancy, partnerships), not temporal changes

**Examples:**
- "JOE CRAWFORD" + "WANDA CRAWFORD" (married couple co-owners)
- "DANNY JOHNSON" + "TIMMY JOHNSON" (family co-owners)

**Model Requirement:** Bridge table `bridge_property_owner` to handle multiple simultaneous owners

**Note:** Some multi-owner records may be name variations ("ASHLEY PRISCILLA" vs "PRISCILLA ASHLEY") requiring entity resolution

---

## Cherre Source Tables

### Primary Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `tax_assessor_v2` | Current property attributes | `tax_assessor_id`, property details, assessed values |
| `tax_assessor_history_v2` | Historical property snapshots | `assessor_snap_shot_year` for SCD Type 2 |
| `recorder_v2` | Transaction records | `recorder_id`, dates, amounts, document types |
| `recorder_grantor_v2` | Seller party details | `grantor_name`, address (38% complete) |
| `recorder_grantee_v2` | Buyer party details | `grantee_name`, address (87% complete) |
| `usa_owner_unmask_v2` | Cherre's canonical entities | `owner_id`, `owner_name`, `cherre_owner_pk` |

### Relationships (Cherre's naming convention)

- **Object relationships:** `<target_object>__<target_field>`
  - Example: `recorder_v2.tax_assessor_v2__tax_assessor_id` links to tax_assessor
- **Array relationships:** Reverse direction
  - Example: `recorder_v2.recorder_grantor_v2__recorder_id` returns array of grantors
- **Bridge tables:** For many-to-many
  - Named: `<object1>_<object2>` (e.g., `tax_assessor_usa_school`)
  - Relationship: `<bridge_table>__bridge`

---

## Data Completeness

### Tax Assessor ID Coverage (Critical for Property Linking)

| Source | Coverage | Sample Size | Notes |
|--------|----------|-------------|-------|
| `recorder_v2` (raw) | **70.2%** | 50,000 records | Direct GraphQL query |
| `cherre_transactions` (processed) | **100%** | All records | Use this for production |

**Strategy:** Use processed `cherre_transactions` table instead of raw `recorder_v2`

### Party Name/Address Completeness

| Field | Completeness | Notes |
|-------|--------------|-------|
| Grantor name | 100% ✅ | Always present |
| Grantee name | 100% ✅ | Always present |
| Grantor address | 38% ⚠️ | Low - harder to match entities |
| Grantee address | 87% ✅ | Good - easier to match |
| Grantor first/last parsed | 80% | Cherre provides parsing |
| Grantee first/last parsed | 79% | Cherre provides parsing |

**Implication:** Entity resolution via name matching is viable. Address matching works better for grantees than grantors.

### Transaction Data Quality

| Field | Completeness | Notes |
|-------|--------------|-------|
| `document_recorded_date` | 100% | Always present |
| `document_amount` | 99% | Present but... |
| `document_amount` > $0 | **26%** | 74% are $0 (mortgages, liens) |
| `arms_length_code` | 77% | Filter for actual sales |

**Note:** Most transactions are not sales (mortgages, liens, title transfers). Filter using `arms_length_code` and `document_amount > 0` for sales analysis.

---

## Entity Resolution Strategy

### Cherre's Approach

Cherre provides `usa_owner_unmask_v2` as their canonical entity layer:
- **`owner_id`:** Composite key format: `{NAME}::{TYPE}::{STATE}::{ADDRESS}`
- **Entity types:** P (Person), I (Institution), G (Government)
- **Linking:** Via `cherre_address` (address-based matching to transactions)

### Our Approach

**Phase 1: Use Cherre's entities**
- Start with `usa_owner_unmask_v2` as base for `dim_entity`
- Parse `owner_id` to extract components for `dim_entity_identifier`

**Phase 2: Extend with transaction parties**
- Match grantor/grantee names to existing entities (exact, then fuzzy)
- Create new identifier records for aliases
- Flag unresolved names for manual review

**Phase 3: Integrate Yardi + NMHC**
- Match Yardi owner names via address (90% coverage expected)
- Link NMHC members via name + entity type
- Enrich entity attributes

### SCD Type 2 Implementation

| Table | Temporal Source | What Changes? |
|-------|----------------|---------------|
| `dim_property` | `tax_assessor_history_v2.assessor_snap_shot_year` | Property attributes (value, sqft, land use) |
| `dim_entity` | Transaction dates + `usa_owner_unmask_v2.last_seen_date` | Entity name, type, state |
| `dim_entity_identifier` | First/last appearance in transactions | When aliases become active/inactive |
| `bridge_property_owner` | Transaction dates (sales) | Ownership start/end dates |

**Key Challenge:** Cherre doesn't provide entity history directly. We must derive it from:
1. Transaction dates (when entity first/last appears as buyer/seller)
2. `last_seen_date` from `usa_owner_unmask_v2`
3. Manual snapshots (if we build ongoing tracking)

---

## Open Questions

1. **Brett's schema alignment:**
   - What structure did Brett create in `canonical_owner_*` tables?
   - Can we merge our dimensional model with his work?

2. **Entity hierarchy:**
   - Do we need to model LLC → Parent Company relationships?
   - How deep does the hierarchy go?

3. **NMHC integration:**
   - What identifiers are in the NMHC file?
   - How do we match to Cherre entities?

4. **Temporal consistency:**
   - How do we handle conflicts (transaction shows sale on 2020-01-01 but tax assessor shows old owner through 2020 year-end)?

5. **Performance:**
   - Bridge tables with history will have high row counts
   - Do we need materialized views for common queries?

---

## Next Steps

1. Review with Brett - align on schema design
2. Understand existing `cherre_transactions` and `canonical_owner_*` tables in Supabase
3. Design ETL strategy (build incrementally vs one-time load)
4. Define entity resolution rules (exact match → fuzzy → manual)
5. Build sample dataset (1,000 records) to test queries
