# NËDL Data Quality

client: nedl
status: active

## Key Context
- Daily standups at 11:30am (started after Dec 12 dry run)
- Brett Summers (contractor) running standups while I'm OOO
- Current state: disaster (see client file for tech details)

### Cherre Data Provider
Cherre (C-H-E-R-R-E) is the aggregated data source. Key questions:
1. Does Cherre provide enough data to be competitive?
2. Are we extracting all fields we're paying for?

Initial findings: data not super complete. Brett doing analysis.

### Field Completeness (Brett's P0 - Dec 16)
- cherre_mf_properties: 94-100% complete
- cherre_avms: 100% complete (527K valuations)
- cherre_mortgages: 89-100% (loan term lowest at 89%)
- cherre_transactions: 2.2M records, 85% of arms-length sales have amounts
- **Status: PASSED** - data quality acceptable

### Data Issues for Cherre
- Some date fields stored as TEXT (cherre_ingest_datetime, data_publish_date, ya_loan_maturity_date)

## Current Todos
- [ ] **P0: Ownership Map** - entity resolution across Cherre unmask + NMHC membership + canonical_owner_* tables. MUST have historicals (SCD Type 2)
- [ ] Text Brett to schedule offline entity-resolution planning session
- [ ] Coordinate w/ Keegan → send Adam Fung availability for **Tuesday**
- [ ] Check via GraphQL if recorder_v2 data (recorder_id + tax_assessor_id) is available in Cherre
- [ ] Delete "Nedl Data Transformation" WhatsApp community → post TLDR to "needle data" group chat
- [ ] Create Mapbox account → get public token (starts with pk.)
- [ ] Set up local env (nedl-app) — repo cloned ✓
- [ ] Improve model prediction accuracy

## In Progress (Brett)
- Building linking table in Supabase
- `canonical_owner_rollup` + `canonical_owner_*` tables created
- ~14k entities across top 100 addresses identified
- Waiting on Stash to send cleaned NMHC membership file

## Parking Lot (not now)
- Alternative data sources (Brett's specialty, but team said no for now)

## Recently Completed
- [x] First standup dry run (Dec 12)
- [x] Get access to all systems (Keegan granted, credentials in .secrets/)
