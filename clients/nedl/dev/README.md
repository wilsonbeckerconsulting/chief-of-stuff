# NËDL Dev Workspace

**Purpose:** Exploratory work, prototypes, testing, analysis for NËDL client work.

## What Lives Here

- **Exploratory scripts** - Testing Cherre API, data analysis, experiments
- **Prototypes** - Entity resolution experiments, data quality checks
- **Ad-hoc queries** - Quick Python scripts to investigate data
- **Test queries** - GraphQL query development and testing
- **Findings** - Document what you learn (see `DATA_MODEL_MAPPING.md`)

## What Does NOT Live Here

- Production pipelines (those go in `nedl-ai` repo)
- Official features (PR those to `nedl-ai`)
- Shared code (that belongs in the official repo)

## Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Install additional packages as needed
pip install pandas jupyter

# Credentials are in config.py (gitignored)
# See .secrets/nedl.md for credential sources
```

---

## Querying Cherre GraphQL - Playbook

### Basic Query Template

```python
#!/usr/bin/env python3
"""
Quick script to query Cherre GraphQL API
"""
import requests
import json
from config import CHERRE_API_KEY, CHERRE_API_URL

def query_cherre(query, variables=None):
    """Execute GraphQL query against Cherre API"""
    headers = {
        "Authorization": f"Basic {CHERRE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post(CHERRE_API_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

# Example usage
if __name__ == "__main__":
    query = """
    query {
        tax_assessor_v2(limit: 5) {
            tax_assessor_id
            property_address
            property_city
            property_state
        }
    }
    """
    result = query_cherre(query)
    print(json.dumps(result, indent=2))
```

### Common Query Patterns

#### 1. Basic Query with Filters

```python
query = """
query {
    recorder_v2(
        limit: 100
        where: {
            property_state: {_eq: "NY"}
            document_recorded_date: {_gte: "2024-01-01"}
        }
    ) {
        recorder_id
        property_address
        document_amount
        document_recorded_date
    }
}
"""
```

#### 2. Nested Relationships (Object - One-to-One)

```python
# Query transactions with property details
query = """
query {
    recorder_v2(limit: 10) {
        recorder_id
        document_amount
        tax_assessor_v2__tax_assessor_id {
            property_address
            property_city
            assessed_value
        }
    }
}
"""
```

**Note:** Cherre's naming convention: `<target_object>__<target_field>` for object relationships

#### 3. Nested Relationships (Array - One-to-Many)

```python
# Query transactions with ALL grantors and grantees
query = """
query {
    recorder_v2(limit: 10) {
        recorder_id
        document_amount
        recorder_grantor_v2__recorder_id {
            grantor_name
            grantor_address
        }
        recorder_grantee_v2__recorder_id {
            grantee_name
            grantee_address
        }
    }
}
"""
```

**Note:** Array relationships return multiple records. Use this for many-to-many cardinality checks.

#### 4. Pagination for Large Datasets

```python
def paginated_query(base_query_template, limit=1000, max_records=10000):
    """Fetch data in chunks"""
    all_results = []
    offset = 0
    
    while offset < max_records:
        query = base_query_template.format(limit=limit, offset=offset)
        result = query_cherre(query)
        
        if not result or 'data' not in result:
            break
        
        # Extract your data (adjust key based on query)
        records = result['data']['recorder_v2']  # or whatever table
        
        if not records:
            break
        
        all_results.extend(records)
        offset += limit
        
        print(f"Fetched {len(all_results)} records so far...")
    
    return all_results

# Usage
query_template = """
query {{
    recorder_v2(limit: {limit}, offset: {offset}) {{
        recorder_id
        tax_assessor_id
        document_recorded_date
    }}
}}
"""

results = paginated_query(query_template, limit=1000, max_records=50000)
```

#### 5. Schema Introspection

```python
# Get all fields for a table
query = """
query {
    __type(name: "recorder_v2") {
        name
        fields {
            name
            type {
                name
                kind
            }
        }
    }
}
"""

# List all available tables
query = """
query {
    __schema {
        queryType {
            fields {
                name
            }
        }
    }
}
"""
```

**Full schema docs:** https://app.cherre.com/core-schema

#### 6. Completeness Check Pattern

```python
def check_completeness(table, field, sample_size=10000):
    """Check how many records have non-null values"""
    query = f"""
    query {{
        {table}(limit: {sample_size}) {{
            {field}
        }}
    }}
    """
    
    result = query_cherre(query)
    records = result['data'][table]
    
    non_null = sum(1 for r in records if r[field] is not None)
    total = len(records)
    pct = (non_null / total * 100) if total > 0 else 0
    
    print(f"{field}: {non_null}/{total} = {pct:.1f}% complete")
    return pct

# Usage
check_completeness('recorder_v2', 'tax_assessor_id', 50000)
check_completeness('recorder_grantor_v2', 'grantor_address', 10000)
```

#### 7. Cardinality Check Pattern

```python
def check_cardinality(limit=1000):
    """Check how many grantors/grantees per transaction"""
    query = f"""
    query {{
        recorder_v2(limit: {limit}) {{
            recorder_id
            recorder_grantor_v2__recorder_id {{
                grantor_name
            }}
            recorder_grantee_v2__recorder_id {{
                grantee_name
            }}
        }}
    }}
    """
    
    result = query_cherre(query)
    transactions = result['data']['recorder_v2']
    
    grantor_dist = {}
    grantee_dist = {}
    
    for txn in transactions:
        g_count = len(txn['recorder_grantor_v2__recorder_id'])
        e_count = len(txn['recorder_grantee_v2__recorder_id'])
        
        grantor_dist[g_count] = grantor_dist.get(g_count, 0) + 1
        grantee_dist[e_count] = grantee_dist.get(e_count, 0) + 1
    
    print("Grantors per transaction:", grantor_dist)
    print("Grantees per transaction:", grantee_dist)

check_cardinality(10000)
```

---

## Common Tasks

### Investigate a specific property

```python
query = """
query {
    tax_assessor_v2(where: {property_address: {_ilike: "%330 EAST 38TH%"}}) {
        tax_assessor_id
        property_address
        assessed_value
        tax_assessor_history_v2__tax_assessor_id {
            assessor_snap_shot_year
            assessed_value
        }
    }
}
"""
```

### Find transactions for a property

```python
query = """
query {
    recorder_v2(where: {tax_assessor_id: {_eq: 12345}}) {
        recorder_id
        document_recorded_date
        document_amount
        recorder_grantor_v2__recorder_id {
            grantor_name
        }
        recorder_grantee_v2__recorder_id {
            grantee_name
        }
    }
}
"""
```

### Look up an entity

```python
query = """
query {
    usa_owner_unmask_v2(where: {owner_name: {_ilike: "%BLACKSTONE%"}}) {
        owner_id
        owner_name
        owner_type
        occurrences_count
        last_seen_date
    }
}
"""
```

---

## Tips & Gotchas

1. **GraphQL errors return 200:** Check for `"errors"` key in response JSON
2. **No aggregate queries:** Cherre doesn't support COUNT(*) or SUM() in GraphQL
3. **Pagination required:** API may have limits (test with small queries first)
4. **Null vs missing:** Empty arrays `[]` are different from `null`
5. **Date formats:** Use ISO format strings `"2024-01-01"` in filters
6. **Case sensitivity:** Field names are case-sensitive, string matching with `_ilike` is not

---

## Files in This Directory

- `config.py` - API credentials (gitignored)
- `CHERRE_DATA_DICTIONARY.md` - Documented Cherre schema fields
- `DATA_MODEL_MAPPING.md` - Findings from data exploration (cardinality, completeness, relationships)
- `venv/` - Python virtual environment

---

## Workflow

1. **Explore here** - Write quick scripts to test hypotheses
2. **Document findings** - Update `DATA_MODEL_MAPPING.md` with validated insights
3. **Brain dump context** - Save notes to `../../raw/` with tags
4. **Build production** - Move validated approaches to `nedl-ai` repo with clean code
