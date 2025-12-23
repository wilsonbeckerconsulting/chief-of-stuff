#!/usr/bin/env python3
"""
NËDL Dimensional Model Builder - 2025 YTD Data
==============================================

Builds complete dimensional model with SCD Type 2 from Cherre GraphQL API:
- dim_property (SCD Type 2)
- dim_entity (SCD Type 2)
- dim_entity_identifier (SCD Type 2, many-to-one)
- fact_transaction (immutable)
- bridge_transaction_party (many-to-many)
- bridge_property_owner (many-to-many, SCD Type 2)

Includes comprehensive data quality validation.

Date Range: January 1, 2025 - December 22, 2025 (YTD)
"""

import requests
import json
import csv
from datetime import datetime
from collections import defaultdict, Counter
from config import CHERRE_API_KEY, CHERRE_API_URL

# ============================================================================
# CONFIGURATION
# ============================================================================

START_DATE = "2025-01-01"
END_DATE = "2025-12-22"
PAGE_SIZE = 1000  # Records per query
MAX_RETRIES = 3

OUTPUT_DIR = "output_2025_ytd"

# Create output directory
import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# GRAPHQL QUERY HELPERS
# ============================================================================

def query_cherre(query, variables=None, retry=0):
    """Execute GraphQL query against Cherre API with retry logic"""
    headers = {
        "Authorization": f"Basic {CHERRE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    try:
        response = requests.post(CHERRE_API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            print(f"⚠️  HTTP {response.status_code}: {response.text[:200]}")
            if retry < MAX_RETRIES:
                print(f"   Retrying ({retry + 1}/{MAX_RETRIES})...")
                return query_cherre(query, variables, retry + 1)
            return None
        
        result = response.json()
        
        if 'errors' in result:
            print(f"⚠️  GraphQL Error: {result['errors']}")
            return None
        
        return result
    
    except Exception as e:
        print(f"⚠️  Request failed: {e}")
        if retry < MAX_RETRIES:
            print(f"   Retrying ({retry + 1}/{MAX_RETRIES})...")
            return query_cherre(query, variables, retry + 1)
        return None

def paginated_query(table_name, fields, where_clause="", order_by="", page_size=PAGE_SIZE, max_records=None):
    """Fetch data with pagination"""
    all_records = []
    offset = 0
    
    print(f"\n📊 Querying {table_name}...")
    
    while True:
        query = f"""
        query {{
            {table_name}(
                limit: {page_size}
                offset: {offset}
                {where_clause}
                {order_by}
            ) {{
                {fields}
            }}
        }}
        """
        
        result = query_cherre(query)
        
        if not result or 'data' not in result or table_name not in result['data']:
            break
        
        records = result['data'][table_name]
        
        if not records:
            break
        
        all_records.extend(records)
        offset += page_size
        
        print(f"   Fetched {len(all_records):,} records...", end='\r')
        
        if max_records and len(all_records) >= max_records:
            all_records = all_records[:max_records]
            break
    
    print(f"   ✅ Fetched {len(all_records):,} total records from {table_name}")
    return all_records

# ============================================================================
# DATA EXTRACTION
# ============================================================================

print("="*80)
print("NËDL DIMENSIONAL MODEL BUILDER - 2025 YTD")
print("="*80)
print(f"Date Range: {START_DATE} to {END_DATE}")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# ----------------------------------------------------------------------------
# 1. TRANSACTIONS (2025 YTD) with nested parties
# ----------------------------------------------------------------------------

print("\n🔍 PHASE 1: Extracting Transactions with Parties")
print("-" * 80)

transactions_raw = paginated_query(
    table_name="recorder_v2",
    fields="""
        recorder_id
        tax_assessor_id
        document_recorded_date
        document_instrument_date
        document_number_formatted
        document_type_code
        document_amount
        transfer_tax_amount
        arms_length_code
        inter_family_flag
        is_foreclosure_auction_sale
        is_quit_claim
        new_construction_flag
        resale_flag
        property_address
        property_city
        property_state
        property_zip
        cherre_ingest_datetime
        recorder_grantor_v2__recorder_id {
            cherre_recorder_grantor_pk
            grantor_name
            grantor_address
            grantor_entity_code
            grantor_first_name
            grantor_last_name
        }
        recorder_grantee_v2__recorder_id {
            cherre_recorder_grantee_pk
            grantee_name
            grantee_address
            grantee_entity_code
            grantee_first_name
            grantee_last_name
        }
    """,
    where_clause=f'where: {{document_recorded_date: {{_gte: "{START_DATE}", _lte: "{END_DATE}"}}}}',
    order_by='order_by: {document_recorded_date: asc}'
)

print(f"\n✅ Extracted {len(transactions_raw):,} transactions for 2025 YTD")

# ----------------------------------------------------------------------------
# 2. PROPERTIES (for all tax_assessor_ids in transactions)
# ----------------------------------------------------------------------------

print("\n🔍 PHASE 2: Extracting Property Data")
print("-" * 80)

# Get unique tax_assessor_ids from transactions
unique_tax_ids = set()
for txn in transactions_raw:
    if txn.get('tax_assessor_id'):
        unique_tax_ids.add(txn['tax_assessor_id'])

print(f"Found {len(unique_tax_ids):,} unique properties in transactions")

# Query properties in batches
properties_raw = []
tax_id_list = list(unique_tax_ids)
batch_size = 500

for i in range(0, len(tax_id_list), batch_size):
    batch = tax_id_list[i:i+batch_size]
    
    query = f"""
    query {{
        tax_assessor_v2(where: {{tax_assessor_id: {{_in: {json.dumps(batch)}}}}}) {{
            tax_assessor_id
            assessor_parcel_number_formatted
            property_address
            property_city
            property_state
            property_zip
            property_county
            property_use_standardized_code
            land_use_code
            year_built
            building_square_feet
            land_square_feet
            units_count
            total_assessed_value
            total_market_value
            latitude
            longitude
        }}
    }}
    """
    
    result = query_cherre(query)
    if result and 'data' in result:
        properties_raw.extend(result['data']['tax_assessor_v2'])
    
    print(f"   Fetched {len(properties_raw):,} properties...", end='\r')

print(f"\n✅ Extracted {len(properties_raw):,} properties")

# ----------------------------------------------------------------------------
# 3. PROPERTY HISTORY (for SCD Type 2)
# ----------------------------------------------------------------------------

print("\n🔍 PHASE 3: Extracting Property History")
print("-" * 80)

property_history_raw = []

for i in range(0, len(tax_id_list), batch_size):
    batch = tax_id_list[i:i+batch_size]
    
    query = f"""
    query {{
        tax_assessor_history_v2(where: {{tax_assessor_id: {{_in: {json.dumps(batch)}}}}}) {{
            tax_assessor_id
            assessor_snap_shot_year
            total_assessed_value
            total_market_value
            land_square_feet
            building_square_feet
        }}
    }}
    """
    
    result = query_cherre(query)
    if result and 'data' in result:
        property_history_raw.extend(result['data']['tax_assessor_history_v2'])
    
    print(f"   Fetched {len(property_history_raw):,} history records...", end='\r')

print(f"\n✅ Extracted {len(property_history_raw):,} property history records")

# ----------------------------------------------------------------------------
# 4. ENTITIES (usa_owner_unmask_v2 for properties in scope)
# ----------------------------------------------------------------------------

print("\n🔍 PHASE 4: Extracting Entity Data")
print("-" * 80)

entities_raw = []

for i in range(0, len(tax_id_list), batch_size):
    batch = tax_id_list[i:i+batch_size]
    
    query = f"""
    query {{
        usa_owner_unmask_v2(where: {{tax_assessor_id: {{_in: {json.dumps(batch)}}}}}) {{
            cherre_usa_owner_unmask_pk
            owner_id
            owner_name
            owner_type
            owner_state
            has_confidence
            occurrences_count
            last_seen_date
            tax_assessor_id
        }}
    }}
    """
    
    result = query_cherre(query)
    if result and 'data' in result:
        entities_raw.extend(result['data']['usa_owner_unmask_v2'])
    
    print(f"   Fetched {len(entities_raw):,} entity records...", end='\r')

print(f"\n✅ Extracted {len(entities_raw):,} entity records")

# ============================================================================
# DATA TRANSFORMATION
# ============================================================================

print("\n" + "="*80)
print("TRANSFORMING DATA INTO DIMENSIONAL MODEL")
print("="*80)

# ----------------------------------------------------------------------------
# BUILD: dim_property (SCD Type 2)
# ----------------------------------------------------------------------------

print("\n🔨 Building dim_property (SCD Type 2)...")

dim_property = []
property_key_counter = 1

# Create property lookup by tax_assessor_id
property_lookup = {p['tax_assessor_id']: p for p in properties_raw}

# Group history by tax_assessor_id
history_by_property = defaultdict(list)
for hist in property_history_raw:
    history_by_property[hist['tax_assessor_id']].append(hist)

for tax_id, prop in property_lookup.items():
    histories = sorted(history_by_property.get(tax_id, []), 
                      key=lambda x: x['assessor_snap_shot_year'])
    
    if histories:
        # Create SCD Type 2 rows from history
        for i, hist in enumerate(histories):
            is_current = (i == len(histories) - 1)
            valid_from = f"{hist['assessor_snap_shot_year']}-01-01"
            valid_to = None if is_current else f"{histories[i+1]['assessor_snap_shot_year']}-01-01"
            
            dim_property.append({
                'property_key': property_key_counter,
                'tax_assessor_id': tax_id,
                'assessor_parcel_number': prop.get('assessor_parcel_number_formatted'),
                'property_address': prop.get('property_address'),
                'property_city': prop.get('property_city'),
                'property_state': prop.get('property_state'),
                'property_zip': prop.get('property_zip'),
                'property_county': prop.get('property_county'),
                'property_use_code': prop.get('property_use_standardized_code'),
                'land_use_code': prop.get('land_use_code'),
                'year_built': prop.get('year_built'),
                'building_sqft': hist.get('building_square_feet') or prop.get('building_square_feet'),
                'land_sqft': hist.get('land_square_feet') or prop.get('land_square_feet'),
                'units_count': prop.get('units_count'),
                'assessed_value': hist.get('total_assessed_value'),
                'market_value': hist.get('total_market_value'),
                'latitude': prop.get('latitude'),
                'longitude': prop.get('longitude'),
                'valid_from': valid_from,
                'valid_to': valid_to,
                'is_current': is_current,
                'source_system': 'cherre'
            })
            property_key_counter += 1
    else:
        # No history - create single current row
        dim_property.append({
            'property_key': property_key_counter,
            'tax_assessor_id': tax_id,
            'assessor_parcel_number': prop.get('assessor_parcel_number_formatted'),
            'property_address': prop.get('property_address'),
            'property_city': prop.get('property_city'),
            'property_state': prop.get('property_state'),
            'property_zip': prop.get('property_zip'),
            'property_county': prop.get('property_county'),
            'property_use_code': prop.get('property_use_standardized_code'),
            'land_use_code': prop.get('land_use_code'),
            'year_built': prop.get('year_built'),
            'building_sqft': prop.get('building_square_feet'),
            'land_sqft': prop.get('land_square_feet'),
            'units_count': prop.get('units_count'),
            'assessed_value': prop.get('total_assessed_value'),
            'market_value': prop.get('total_market_value'),
            'latitude': prop.get('latitude'),
            'longitude': prop.get('longitude'),
            'valid_from': '2025-01-01',  # Default to year start
            'valid_to': None,
            'is_current': True,
            'source_system': 'cherre'
        })
        property_key_counter += 1

print(f"✅ Created {len(dim_property):,} dim_property records (with SCD Type 2)")

# Create lookup: tax_assessor_id → current property_key
property_key_lookup = {}
for prop in dim_property:
    if prop['is_current']:
        property_key_lookup[prop['tax_assessor_id']] = prop['property_key']

# ----------------------------------------------------------------------------
# BUILD: dim_entity (SCD Type 2)
# ----------------------------------------------------------------------------

print("\n🔨 Building dim_entity (SCD Type 2)...")

dim_entity = []
entity_key_counter = 1

# Group entities by owner_id (canonical ID)
entities_by_owner_id = defaultdict(list)
for ent in entities_raw:
    if ent.get('owner_id'):
        entities_by_owner_id[ent['owner_id']].append(ent)

for owner_id, ent_records in entities_by_owner_id.items():
    # Take first record as base (they should be duplicates)
    base = ent_records[0]
    
    # Calculate confidence score
    confidence = 0
    if base.get('has_confidence'):
        confidence += 50
    
    occ = base.get('occurrences_count') or 0
    if occ >= 10:
        confidence += 50
    elif occ >= 5:
        confidence += 30
    elif occ >= 2:
        confidence += 20
    else:
        confidence += 10
    
    # For now, create single current record (TODO: derive temporal from transactions)
    dim_entity.append({
        'entity_key': entity_key_counter,
        'canonical_entity_id': owner_id,
        'cherre_owner_pk': base.get('cherre_usa_owner_unmask_pk'),
        'canonical_entity_name': base.get('owner_name'),
        'entity_type': base.get('owner_type'),
        'state': base.get('owner_state'),
        'confidence_score': confidence,
        'occurrences_count': base.get('occurrences_count'),
        'is_resolved': True,
        'resolution_method': 'cherre',
        'valid_from': '2025-01-01',  # TODO: derive from first transaction
        'valid_to': base.get('last_seen_date'),
        'is_current': True,  # Simplified for now
        'source_system': 'cherre'
    })
    
    entity_key_counter += 1

print(f"✅ Created {len(dim_entity):,} dim_entity records")

# Create lookup: owner_id → entity_key
entity_key_lookup = {e['canonical_entity_id']: e['entity_key'] for e in dim_entity}

# ----------------------------------------------------------------------------
# BUILD: dim_entity_identifier
# ----------------------------------------------------------------------------

print("\n🔨 Building dim_entity_identifier...")

dim_entity_identifier = []
identifier_key_counter = 1

# Add identifiers from usa_owner_unmask_v2
for ent in dim_entity:
    owner_id = ent['canonical_entity_id']
    entity_key = ent['entity_key']
    
    # Parse composite owner_id: "NAME::TYPE::STATE::ADDRESS"
    parts = owner_id.split("::")
    
    # Full owner_id
    dim_entity_identifier.append({
        'identifier_key': identifier_key_counter,
        'entity_key': entity_key,
        'identifier_type': 'cherre_owner_id',
        'identifier_value': owner_id,
        'source_system': 'cherre',
        'source_table': 'usa_owner_unmask_v2',
        'is_primary': True,
        'valid_from': ent['valid_from'],
        'valid_to': ent['valid_to'],
        'is_current': True
    })
    identifier_key_counter += 1
    
    # Owner name
    if len(parts) > 0 and parts[0]:
        dim_entity_identifier.append({
            'identifier_key': identifier_key_counter,
            'entity_key': entity_key,
            'identifier_type': 'owner_name',
            'identifier_value': parts[0],
            'source_system': 'cherre',
            'source_table': 'usa_owner_unmask_v2',
            'is_primary': False,
            'valid_from': ent['valid_from'],
            'valid_to': ent['valid_to'],
            'is_current': True
        })
        identifier_key_counter += 1

print(f"✅ Created {len(dim_entity_identifier):,} dim_entity_identifier records")

# ----------------------------------------------------------------------------
# BUILD: fact_transaction
# ----------------------------------------------------------------------------

print("\n🔨 Building fact_transaction...")

fact_transaction = []
transaction_key_counter = 1

for txn in transactions_raw:
    # Classify transaction
    is_sale = False
    transaction_category = 'OTHER'
    
    if txn.get('arms_length_code') and txn.get('document_amount') and txn['document_amount'] > 0:
        is_sale = True
        transaction_category = 'SALE'
    elif txn.get('document_amount') == 0:
        transaction_category = 'MORTGAGE'  # Simplified
    
    # Get property_key
    property_key = None
    if txn.get('tax_assessor_id'):
        property_key = property_key_lookup.get(txn['tax_assessor_id'])
    
    # Count parties
    grantor_count = len(txn.get('recorder_grantor_v2__recorder_id', []))
    grantee_count = len(txn.get('recorder_grantee_v2__recorder_id', []))
    
    fact_transaction.append({
        'transaction_key': transaction_key_counter,
        'recorder_id': txn['recorder_id'],
        'property_key': property_key,
        'transaction_date': txn.get('document_recorded_date'),
        'instrument_date': txn.get('document_instrument_date'),
        'document_number': txn.get('document_number_formatted'),
        'document_type_code': txn.get('document_type_code'),
        'document_amount': txn.get('document_amount'),
        'transfer_tax_amount': txn.get('transfer_tax_amount'),
        'arms_length_flag': txn.get('arms_length_code'),
        'inter_family_flag': txn.get('inter_family_flag'),
        'is_foreclosure': txn.get('is_foreclosure_auction_sale'),
        'is_quit_claim': txn.get('is_quit_claim'),
        'new_construction_flag': txn.get('new_construction_flag'),
        'resale_flag': txn.get('resale_flag'),
        'transaction_category': transaction_category,
        'is_sale': is_sale,
        'property_address': txn.get('property_address'),
        'property_city': txn.get('property_city'),
        'property_state': txn.get('property_state'),
        'property_zip': txn.get('property_zip'),
        'tax_assessor_id': txn.get('tax_assessor_id'),
        'grantor_count': grantor_count,
        'grantee_count': grantee_count,
        'has_multiple_parties': (grantor_count + grantee_count) > 2,
        'source_system': 'cherre',
        'cherre_ingest_datetime': txn.get('cherre_ingest_datetime')
    })
    
    transaction_key_counter += 1

print(f"✅ Created {len(fact_transaction):,} fact_transaction records")

# Create lookup: recorder_id → transaction_key
transaction_key_lookup = {t['recorder_id']: t['transaction_key'] for t in fact_transaction}

# ----------------------------------------------------------------------------
# BUILD: bridge_transaction_party
# ----------------------------------------------------------------------------

print("\n🔨 Building bridge_transaction_party (many-to-many)...")

bridge_transaction_party = []
bridge_tp_key_counter = 1

for txn in transactions_raw:
    transaction_key = transaction_key_lookup.get(txn['recorder_id'])
    if not transaction_key:
        continue
    
    # Grantors (sellers)
    for seq, grantor in enumerate(txn.get('recorder_grantor_v2__recorder_id', []), 1):
        bridge_transaction_party.append({
            'bridge_key': bridge_tp_key_counter,
            'transaction_key': transaction_key,
            'entity_key': None,  # TODO: entity resolution
            'party_role': 'grantor',
            'party_sequence': seq,
            'party_name_raw': grantor.get('grantor_name'),
            'party_address_raw': grantor.get('grantor_address'),
            'party_entity_code': grantor.get('grantor_entity_code'),
            'is_resolved': False,
            'resolution_method': None,
            'source_table': 'recorder_grantor_v2',
            'source_record_pk': grantor.get('cherre_recorder_grantor_pk')
        })
        bridge_tp_key_counter += 1
    
    # Grantees (buyers)
    for seq, grantee in enumerate(txn.get('recorder_grantee_v2__recorder_id', []), 1):
        bridge_transaction_party.append({
            'bridge_key': bridge_tp_key_counter,
            'transaction_key': transaction_key,
            'entity_key': None,  # TODO: entity resolution
            'party_role': 'grantee',
            'party_sequence': seq,
            'party_name_raw': grantee.get('grantee_name'),
            'party_address_raw': grantee.get('grantee_address'),
            'party_entity_code': grantee.get('grantee_entity_code'),
            'is_resolved': False,
            'resolution_method': None,
            'source_table': 'recorder_grantee_v2',
            'source_record_pk': grantee.get('cherre_recorder_grantee_pk')
        })
        bridge_tp_key_counter += 1

print(f"✅ Created {len(bridge_transaction_party):,} bridge_transaction_party records")

# ----------------------------------------------------------------------------
# BUILD: bridge_property_owner (many-to-many, SCD Type 2)
# ----------------------------------------------------------------------------

print("\n🔨 Building bridge_property_owner (many-to-many with SCD Type 2)...")

bridge_property_owner = []
bridge_po_key_counter = 1

# Group entities by tax_assessor_id
owners_by_property = defaultdict(list)
for ent in entities_raw:
    if ent.get('tax_assessor_id') and ent.get('owner_id'):
        owners_by_property[ent['tax_assessor_id']].append(ent)

for tax_id, owners in owners_by_property.items():
    property_key = property_key_lookup.get(tax_id)
    if not property_key:
        continue
    
    for seq, owner in enumerate(owners, 1):
        entity_key = entity_key_lookup.get(owner['owner_id'])
        if not entity_key:
            continue
        
        bridge_property_owner.append({
            'bridge_key': bridge_po_key_counter,
            'property_key': property_key,
            'entity_key': entity_key,
            'ownership_sequence': seq,
            'ownership_percentage': None,  # Not provided by Cherre
            'ownership_type': None,  # TODO: infer from entity_type
            'valid_from': '2025-01-01',  # Simplified
            'valid_to': owner.get('last_seen_date'),
            'is_current': True,  # Simplified
            'is_derived': False
        })
        bridge_po_key_counter += 1

print(f"✅ Created {len(bridge_property_owner):,} bridge_property_owner records")

# ============================================================================
# WRITE CSV FILES
# ============================================================================

print("\n" + "="*80)
print("WRITING CSV FILES")
print("="*80)

def write_csv(filename, data, fieldnames):
    """Write list of dicts to CSV"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ {filename}: {len(data):,} rows")

write_csv('dim_property.csv', dim_property, [
    'property_key', 'tax_assessor_id', 'assessor_parcel_number', 'property_address',
    'property_city', 'property_state', 'property_zip', 'property_county',
    'property_use_code', 'land_use_code', 'year_built', 'building_sqft', 'land_sqft',
    'units_count', 'assessed_value', 'market_value', 'latitude', 'longitude',
    'valid_from', 'valid_to', 'is_current', 'source_system'
])

write_csv('dim_entity.csv', dim_entity, [
    'entity_key', 'canonical_entity_id', 'cherre_owner_pk', 'canonical_entity_name',
    'entity_type', 'state', 'confidence_score', 'occurrences_count', 'is_resolved',
    'resolution_method', 'valid_from', 'valid_to', 'is_current', 'source_system'
])

write_csv('dim_entity_identifier.csv', dim_entity_identifier, [
    'identifier_key', 'entity_key', 'identifier_type', 'identifier_value',
    'source_system', 'source_table', 'is_primary', 'valid_from', 'valid_to', 'is_current'
])

write_csv('fact_transaction.csv', fact_transaction, [
    'transaction_key', 'recorder_id', 'property_key', 'transaction_date', 'instrument_date',
    'document_number', 'document_type_code', 'document_amount', 'transfer_tax_amount',
    'arms_length_flag', 'inter_family_flag', 'is_foreclosure', 'is_quit_claim',
    'new_construction_flag', 'resale_flag', 'transaction_category', 'is_sale',
    'property_address', 'property_city', 'property_state', 'property_zip', 'tax_assessor_id',
    'grantor_count', 'grantee_count', 'has_multiple_parties', 'source_system', 'cherre_ingest_datetime'
])

write_csv('bridge_transaction_party.csv', bridge_transaction_party, [
    'bridge_key', 'transaction_key', 'entity_key', 'party_role', 'party_sequence',
    'party_name_raw', 'party_address_raw', 'party_entity_code', 'is_resolved',
    'resolution_method', 'source_table', 'source_record_pk'
])

write_csv('bridge_property_owner.csv', bridge_property_owner, [
    'bridge_key', 'property_key', 'entity_key', 'ownership_sequence', 'ownership_percentage',
    'ownership_type', 'valid_from', 'valid_to', 'is_current', 'is_derived'
])

# ============================================================================
# DATA QUALITY VALIDATION & STATISTICS
# ============================================================================

print("\n" + "="*80)
print("DATA QUALITY VALIDATION & STATISTICS")
print("="*80)

dq_report = []
statistics = []

def dq_check(category, check_name, passed, total, message="", threshold=100):
    """Record DQ check result - validates model assumptions"""
    pct = (passed / total * 100) if total > 0 else 0
    status = "✅ PASS" if pct >= threshold else "⚠️  WARN" if pct >= (threshold - 15) else "❌ FAIL"
    
    result = {
        'category': category,
        'check': check_name,
        'status': status,
        'passed': passed,
        'total': total,
        'percentage': f"{pct:.1f}%",
        'message': message
    }
    dq_report.append(result)
    
    print(f"{status} | {category:20s} | {check_name:40s} | {passed:,}/{total:,} ({pct:.1f}%)")
    if message:
        print(f"      └─ {message}")

def record_stat(category, metric, value, description=""):
    """Record statistical finding - no pass/fail, just informational"""
    result = {
        'category': category,
        'metric': metric,
        'value': value,
        'description': description
    }
    statistics.append(result)
    
    print(f"📊 STAT | {category:20s} | {metric:40s} | {value}")
    if description:
        print(f"      └─ {description}")

print("\n--- MODEL ASSUMPTION: REQUIRED FIELDS (NOT NULL) ---\n")

# dim_property required fields
dq_check('REQUIRED_FIELD', 'dim_property.tax_assessor_id NOT NULL',
         sum(1 for p in dim_property if p.get('tax_assessor_id')), len(dim_property),
         threshold=100)
dq_check('REQUIRED_FIELD', 'dim_property.valid_from NOT NULL',
         sum(1 for p in dim_property if p.get('valid_from')), len(dim_property),
         threshold=100)

# dim_entity required fields
dq_check('REQUIRED_FIELD', 'dim_entity.canonical_entity_id NOT NULL',
         sum(1 for e in dim_entity if e.get('canonical_entity_id')), len(dim_entity),
         threshold=100)
dq_check('REQUIRED_FIELD', 'dim_entity.canonical_entity_name NOT NULL',
         sum(1 for e in dim_entity if e.get('canonical_entity_name')), len(dim_entity),
         threshold=100)

# fact_transaction required fields
dq_check('REQUIRED_FIELD', 'fact_transaction.recorder_id NOT NULL',
         sum(1 for t in fact_transaction if t.get('recorder_id')), len(fact_transaction),
         threshold=100)
dq_check('REQUIRED_FIELD', 'fact_transaction.transaction_date NOT NULL',
         sum(1 for t in fact_transaction if t.get('transaction_date')), len(fact_transaction),
         threshold=100)

# bridge_transaction_party required fields
dq_check('REQUIRED_FIELD', 'bridge_transaction_party.party_name_raw NOT NULL',
         sum(1 for b in bridge_transaction_party if b.get('party_name_raw')), len(bridge_transaction_party),
         threshold=100)

print("\n--- COMPLETENESS STATISTICS (Optional Fields) ---\n")

# Optional fields - just report completeness, no pass/fail
if len(dim_property) > 0:
    prop_addr_complete = sum(1 for p in dim_property if p.get('property_address'))
    record_stat('COMPLETENESS', 'dim_property.property_address',
                f"{prop_addr_complete:,}/{len(dim_property):,} ({prop_addr_complete/len(dim_property)*100:.1f}%)")
else:
    record_stat('COMPLETENESS', 'dim_property.property_address', 'N/A - no data')

if len(fact_transaction) > 0:
    prop_key_complete = sum(1 for t in fact_transaction if t.get('property_key'))
    record_stat('COMPLETENESS', 'fact_transaction.property_key',
                f"{prop_key_complete:,}/{len(fact_transaction):,} ({prop_key_complete/len(fact_transaction)*100:.1f}%)",
                "Depends on tax_assessor_id availability in source data")
else:
    record_stat('COMPLETENESS', 'fact_transaction.property_key', 'N/A - no data')

if len(bridge_transaction_party) > 0:
    party_addr_complete = sum(1 for b in bridge_transaction_party if b.get('party_address_raw'))
    record_stat('COMPLETENESS', 'bridge_transaction_party.party_address_raw',
                f"{party_addr_complete:,}/{len(bridge_transaction_party):,} ({party_addr_complete/len(bridge_transaction_party)*100:.1f}%)")
else:
    record_stat('COMPLETENESS', 'bridge_transaction_party.party_address_raw', 'N/A - no data')

print("\n--- MODEL ASSUMPTION: PRIMARY KEY UNIQUENESS ---\n")

# Primary key uniqueness - MUST be 100% for model to work
dq_check('UNIQUENESS', 'dim_property.property_key is unique',
         len(set(p['property_key'] for p in dim_property)), len(dim_property),
         threshold=100)
dq_check('UNIQUENESS', 'dim_entity.entity_key is unique',
         len(set(e['entity_key'] for e in dim_entity)), len(dim_entity),
         threshold=100)
dq_check('UNIQUENESS', 'fact_transaction.transaction_key is unique',
         len(set(t['transaction_key'] for t in fact_transaction)), len(fact_transaction),
         threshold=100)
dq_check('UNIQUENESS', 'fact_transaction.recorder_id is unique',
         len(set(t['recorder_id'] for t in fact_transaction)), len(fact_transaction),
         threshold=100)

# Natural key uniqueness (SCD Type 2 - tax_assessor_id + valid_from) - MUST be unique
unique_prop_nk = set()
for p in dim_property:
    nk = (p['tax_assessor_id'], p['valid_from'])
    unique_prop_nk.add(nk)
dq_check('UNIQUENESS', 'dim_property (tax_assessor_id, valid_from) is unique',
         len(unique_prop_nk), len(dim_property),
         threshold=100,
         message="SCD Type 2 natural key must be unique")

print("\n--- MODEL ASSUMPTION: REFERENTIAL INTEGRITY (Foreign Keys) ---\n")

# fact_transaction.property_key → dim_property.property_key
# Only check records WHERE property_key IS NOT NULL
valid_property_keys = set(p['property_key'] for p in dim_property)
txns_with_prop_key = [t for t in fact_transaction if t.get('property_key')]
valid_fk_count = sum(1 for t in txns_with_prop_key if t['property_key'] in valid_property_keys)
dq_check('REFERENTIAL_INTEGRITY', 'fact_transaction.property_key → dim_property',
         valid_fk_count, 
         len(txns_with_prop_key),
         threshold=100,
         message="All non-null FKs must exist in parent table")

# bridge_transaction_party.transaction_key → fact_transaction.transaction_key
valid_txn_keys = set(t['transaction_key'] for t in fact_transaction)
valid_bridge_tp = sum(1 for b in bridge_transaction_party 
                      if b['transaction_key'] in valid_txn_keys)
dq_check('REFERENTIAL_INTEGRITY', 'bridge_transaction_party.transaction_key → fact_transaction',
         valid_bridge_tp, len(bridge_transaction_party),
         threshold=100)

# bridge_property_owner.property_key → dim_property.property_key
valid_bridge_po_prop = sum(1 for b in bridge_property_owner 
                           if b['property_key'] in valid_property_keys)
dq_check('REFERENTIAL_INTEGRITY', 'bridge_property_owner.property_key → dim_property',
         valid_bridge_po_prop, len(bridge_property_owner),
         threshold=100)

# bridge_property_owner.entity_key → dim_entity.entity_key
valid_entity_keys = set(e['entity_key'] for e in dim_entity)
valid_bridge_po_ent = sum(1 for b in bridge_property_owner 
                          if b['entity_key'] in valid_entity_keys)
dq_check('REFERENTIAL_INTEGRITY', 'bridge_property_owner.entity_key → dim_entity',
         valid_bridge_po_ent, len(bridge_property_owner),
         threshold=100)

print("\n--- CARDINALITY STATISTICS (Distributions) ---\n")

# Transaction → Party cardinality
grantor_dist = Counter()
grantee_dist = Counter()

for txn in fact_transaction:
    grantor_dist[txn['grantor_count']] += 1
    grantee_dist[txn['grantee_count']] += 1

print("Grantors per transaction:")
for count in sorted(grantor_dist.keys()):
    pct = grantor_dist[count] / len(fact_transaction) * 100
    record_stat('CARDINALITY', f'  {count} grantor(s)', f"{grantor_dist[count]:>7,} ({pct:>5.1f}%)")

multi_grantor_count = sum(count for g_count, count in grantor_dist.items() if g_count >= 2)
multi_grantor_pct = multi_grantor_count / len(fact_transaction) * 100
record_stat('CARDINALITY', 'Transactions with 2+ grantors', 
            f"{multi_grantor_count:,}/{len(fact_transaction):,} ({multi_grantor_pct:.1f}%)")

print("\nGrantees per transaction:")
for count in sorted(grantee_dist.keys()):
    pct = grantee_dist[count] / len(fact_transaction) * 100
    record_stat('CARDINALITY', f'  {count} grantee(s)', f"{grantee_dist[count]:>7,} ({pct:>5.1f}%)")

multi_grantee_count = sum(count for g_count, count in grantee_dist.items() if g_count >= 2)
multi_grantee_pct = multi_grantee_count / len(fact_transaction) * 100
record_stat('CARDINALITY', 'Transactions with 2+ grantees',
            f"{multi_grantee_count:,}/{len(fact_transaction):,} ({multi_grantee_pct:.1f}%)")

# Property → Owner cardinality
owners_per_property = Counter()
for prop_key in set(b['property_key'] for b in bridge_property_owner):
    owner_count = sum(1 for b in bridge_property_owner if b['property_key'] == prop_key)
    owners_per_property[owner_count] += 1

print("\nOwners per property:")
for count in sorted(owners_per_property.keys()):
    total_props = sum(owners_per_property.values())
    pct = owners_per_property[count] / total_props * 100 if total_props else 0
    record_stat('CARDINALITY', f'  {count} owner(s)', f"{owners_per_property[count]:>7,} ({pct:>5.1f}%)")

multi_owner_count = sum(count for o_count, count in owners_per_property.items() if o_count >= 2)
multi_owner_pct = multi_owner_count / sum(owners_per_property.values()) * 100 if owners_per_property else 0
record_stat('CARDINALITY', 'Properties with 2+ owners',
            f"{multi_owner_count:,}/{sum(owners_per_property.values()):,} ({multi_owner_pct:.1f}%)")

print("\n--- MODEL ASSUMPTION: DATA CONSISTENCY ---\n")

# SCD Type 2: is_current flag consistency - MUST have only 1 current row per natural key
current_props = sum(1 for p in dim_property if p['is_current'])
unique_current_tax_ids = len(set(p['tax_assessor_id'] for p in dim_property if p['is_current']))
dq_check('CONSISTENCY', 'dim_property: 1 current row per tax_assessor_id',
         unique_current_tax_ids, current_props,
         threshold=100,
         message=f"{current_props - unique_current_tax_ids} duplicate current rows" if current_props != unique_current_tax_ids else "✓ No duplicate current rows")

# Bridge table party counts MUST match fact table aggregates
bridge_grantor_count = sum(1 for b in bridge_transaction_party if b['party_role'] == 'grantor')
fact_grantor_sum = sum(t['grantor_count'] for t in fact_transaction)
matches = (bridge_grantor_count == fact_grantor_sum)
dq_check('CONSISTENCY', 'bridge_transaction_party grantor count = fact.grantor_count sum',
         fact_grantor_sum if matches else 0, fact_grantor_sum,
         threshold=100,
         message=f"Bridge: {bridge_grantor_count:,}, Fact sum: {fact_grantor_sum:,}")

bridge_grantee_count = sum(1 for b in bridge_transaction_party if b['party_role'] == 'grantee')
fact_grantee_sum = sum(t['grantee_count'] for t in fact_transaction)
matches = (bridge_grantee_count == fact_grantee_sum)
dq_check('CONSISTENCY', 'bridge_transaction_party grantee count = fact.grantee_count sum',
         fact_grantee_sum if matches else 0, fact_grantee_sum,
         threshold=100,
         message=f"Bridge: {bridge_grantee_count:,}, Fact sum: {fact_grantee_sum:,}")

# Date range validation - all transactions MUST be in expected range
txn_dates = [t['transaction_date'] for t in fact_transaction if t.get('transaction_date')]
if txn_dates:
    min_date = min(txn_dates)
    max_date = max(txn_dates)
    dates_in_range = sum(1 for d in txn_dates if START_DATE <= d <= END_DATE)
    dq_check('CONSISTENCY', f'Transactions within expected date range',
             dates_in_range, len(txn_dates),
             threshold=100,
             message=f"Expected: {START_DATE} to {END_DATE}, Actual: {min_date} to {max_date}")

print("\n--- MODEL ASSUMPTION: BUSINESS LOGIC ---\n")

# Sales transactions (is_sale=TRUE) MUST have amount > 0 by definition
sales = [t for t in fact_transaction if t['is_sale']]
sales_with_amount = sum(1 for t in sales if t.get('document_amount') and t['document_amount'] > 0)
dq_check('BUSINESS_LOGIC', 'Sales (is_sale=TRUE) have document_amount > 0',
         sales_with_amount, len(sales),
         threshold=100,
         message="Sales classification requires non-zero amount")

# Every transaction should have at least one party (grantor OR grantee)
txns_with_parties = sum(1 for t in fact_transaction if t['grantor_count'] > 0 or t['grantee_count'] > 0)
dq_check('BUSINESS_LOGIC', 'Transactions have at least one party',
         txns_with_parties, len(fact_transaction),
         threshold=95,
         message="Some transactions may be data quality issues if no parties")

print("\n--- TRANSACTION TYPE STATISTICS ---\n")

# Transaction category breakdown
category_dist = Counter(t['transaction_category'] for t in fact_transaction)
for category in sorted(category_dist.keys()):
    pct = category_dist[category] / len(fact_transaction) * 100
    record_stat('TRANSACTION_TYPE', f'{category} transactions', 
                f"{category_dist[category]:>7,} ({pct:>5.1f}%)")

# Sales breakdown
sales_count = len(sales)
sales_pct = sales_count / len(fact_transaction) * 100
record_stat('TRANSACTION_TYPE', 'Total sales (is_sale=TRUE)', 
            f"{sales_count:,}/{len(fact_transaction):,} ({sales_pct:.1f}%)")

# Document amounts
zero_amount = sum(1 for t in fact_transaction if t.get('document_amount') == 0)
null_amount = sum(1 for t in fact_transaction if t.get('document_amount') is None)
positive_amount = sum(1 for t in fact_transaction if t.get('document_amount') and t['document_amount'] > 0)
record_stat('TRANSACTION_TYPE', 'Transactions with $0 amount',
            f"{zero_amount:,}/{len(fact_transaction):,} ({zero_amount/len(fact_transaction)*100:.1f}%)")
record_stat('TRANSACTION_TYPE', 'Transactions with NULL amount',
            f"{null_amount:,}/{len(fact_transaction):,} ({null_amount/len(fact_transaction)*100:.1f}%)")
record_stat('TRANSACTION_TYPE', 'Transactions with amount > $0',
            f"{positive_amount:,}/{len(fact_transaction):,} ({positive_amount/len(fact_transaction)*100:.1f}%)")

# ============================================================================
# GENERATE DQ REPORT & STATISTICS
# ============================================================================

print("\n" + "="*80)
print("GENERATING REPORTS")
print("="*80)

# Write DQ report CSV (validation checks only)
dq_filepath = os.path.join(OUTPUT_DIR, 'DQ_VALIDATION_REPORT.csv')
with open(dq_filepath, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['category', 'check', 'status', 'passed', 'total', 'percentage', 'message']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(dq_report)

print(f"✅ DQ_VALIDATION_REPORT.csv: {len(dq_report)} validation checks")

# Write statistics CSV (distributions and metrics)
stats_filepath = os.path.join(OUTPUT_DIR, 'STATISTICS_REPORT.csv')
with open(stats_filepath, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['category', 'metric', 'value', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(statistics)

print(f"✅ STATISTICS_REPORT.csv: {len(statistics)} metrics")

# Summary statistics
summary_filepath = os.path.join(OUTPUT_DIR, 'SUMMARY.txt')
with open(summary_filepath, 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("NËDL DIMENSIONAL MODEL - 2025 YTD SUMMARY\n")
    f.write("="*80 + "\n\n")
    
    f.write(f"Date Range: {START_DATE} to {END_DATE}\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("--- TABLE ROW COUNTS ---\n\n")
    f.write(f"dim_property:              {len(dim_property):>10,} rows\n")
    f.write(f"dim_entity:                {len(dim_entity):>10,} rows\n")
    f.write(f"dim_entity_identifier:     {len(dim_entity_identifier):>10,} rows\n")
    f.write(f"fact_transaction:          {len(fact_transaction):>10,} rows\n")
    f.write(f"bridge_transaction_party:  {len(bridge_transaction_party):>10,} rows\n")
    f.write(f"bridge_property_owner:     {len(bridge_property_owner):>10,} rows\n\n")
    
    f.write("--- DATA QUALITY VALIDATION SUMMARY ---\n\n")
    
    fail_count = sum(1 for r in dq_report if r['status'] == '❌ FAIL')
    warn_count = sum(1 for r in dq_report if r['status'] == '⚠️  WARN')
    pass_count = sum(1 for r in dq_report if r['status'] == '✅ PASS')
    
    f.write(f"Total Validation Checks:  {len(dq_report)}\n")
    f.write(f"✅ Passed:                {pass_count}\n")
    f.write(f"⚠️  Warnings:              {warn_count}\n")
    f.write(f"❌ Failed:                {fail_count}\n\n")
    
    if fail_count > 0:
        f.write("❌ FAILED CHECKS (Model assumptions violated):\n")
        for r in dq_report:
            if r['status'] == '❌ FAIL':
                f.write(f"  - {r['category']}: {r['check']} ({r['percentage']})\n")
                if r.get('message'):
                    f.write(f"    → {r['message']}\n")
        f.write("\n")
    
    if warn_count > 0:
        f.write("⚠️  WARNINGS (Review recommended):\n")
        for r in dq_report:
            if r['status'] == '⚠️  WARN':
                f.write(f"  - {r['category']}: {r['check']} ({r['percentage']})\n")
                if r.get('message'):
                    f.write(f"    → {r['message']}\n")
        f.write("\n")
    
    f.write("--- KEY METRICS ---\n\n")
    f.write(f"Unique properties:         {len(set(p['tax_assessor_id'] for p in dim_property)):>10,}\n")
    f.write(f"Unique entities:           {len(dim_entity):>10,}\n")
    f.write(f"Transactions with parties: {len(set(b['transaction_key'] for b in bridge_transaction_party)):>10,}\n")
    f.write(f"Sales transactions:        {len([t for t in fact_transaction if t['is_sale']]):>10,}\n")
    f.write(f"Properties with owners:    {len(set(b['property_key'] for b in bridge_property_owner)):>10,}\n\n")
    
    f.write("--- CARDINALITY FINDINGS ---\n\n")
    f.write(f"Grantors per transaction:\n")
    for count in sorted(grantor_dist.keys()):
        pct = grantor_dist[count] / len(fact_transaction) * 100
        f.write(f"  {count}: {grantor_dist[count]:>7,} ({pct:>5.1f}%)\n")
    
    f.write(f"\nGrantees per transaction:\n")
    for count in sorted(grantee_dist.keys()):
        pct = grantee_dist[count] / len(fact_transaction) * 100
        f.write(f"  {count}: {grantee_dist[count]:>7,} ({pct:>5.1f}%)\n")
    
    f.write(f"\nOwners per property:\n")
    for count in sorted(owners_per_property.keys()):
        pct = owners_per_property[count] / sum(owners_per_property.values()) * 100
        f.write(f"  {count}: {owners_per_property[count]:>7,} ({pct:>5.1f}%)\n")

print(f"✅ SUMMARY.txt")

print("\n" + "="*80)
print("BUILD COMPLETE!")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR}/")
print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Final summary
print("OUTPUT FILES:")
print("  📊 Data Files:")
print("     - dim_property.csv")
print("     - dim_entity.csv")
print("     - dim_entity_identifier.csv")
print("     - fact_transaction.csv")
print("     - bridge_transaction_party.csv")
print("     - bridge_property_owner.csv")
print("  📋 Reports:")
print("     - DQ_VALIDATION_REPORT.csv (validation checks)")
print("     - STATISTICS_REPORT.csv (distributions & metrics)")
print("     - SUMMARY.txt (executive summary)")
print()

print("DATA QUALITY VALIDATION:")
print(f"  ✅ Passed:   {pass_count}/{len(dq_report)}")
print(f"  ⚠️  Warnings: {warn_count}/{len(dq_report)}")
print(f"  ❌ Failed:   {fail_count}/{len(dq_report)}")
print()

if fail_count > 0:
    print("❌ CRITICAL: Some validation checks failed. Model assumptions may be violated.")
    print("   Review DQ_VALIDATION_REPORT.csv for details.")
    print()
elif warn_count > 0:
    print("⚠️  WARNINGS: Some checks show potential issues. Review recommended.")
    print("   Check DQ_VALIDATION_REPORT.csv for details.")
    print()
else:
    print("✅ SUCCESS: All validation checks passed! Model assumptions are satisfied.")
    print()

print(f"📊 Statistics collected: {len(statistics)} metrics")
print(f"   Review STATISTICS_REPORT.csv for data distributions.")
print()

