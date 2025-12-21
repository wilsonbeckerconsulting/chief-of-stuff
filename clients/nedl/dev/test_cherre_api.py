#!/usr/bin/env python3
"""
Test script to verify Cherre API access and explore GraphQL queries.

Usage:
    python test_cherre_api.py
"""

import json
import requests
from config import CHERRE_API_KEY, CHERRE_API_URL


def test_simple_query():
    """Test basic Cherre API access with a simple tax_assessor query."""
    
    query = """
    query TestQuery {
      tax_assessor_v2(
        where: {
          city: {_eq: "CHICAGO"}
          state: {_eq: "IL"}
        }
        limit: 5
      ) {
        tax_assessor_id
        address
        city
        state
        zip
      }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {CHERRE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    
    print("Testing Cherre API access...")
    print(f"Endpoint: {CHERRE_API_URL}")
    print(f"Query: {query.strip()}\n")
    
    try:
        response = requests.post(CHERRE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            print("❌ GraphQL Errors:")
            print(json.dumps(data["errors"], indent=2))
            return False
        
        if "data" in data and data["data"]["tax_assessor_v2"]:
            print("✅ API Access Successful!")
            print(f"\nReturned {len(data['data']['tax_assessor_v2'])} properties:")
            print(json.dumps(data["data"]["tax_assessor_v2"], indent=2))
            return True
        else:
            print("⚠️  No data returned (but no errors)")
            print(json.dumps(data, indent=2))
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


def test_recorder_v2_availability():
    """
    Test if recorder_v2 data is available with recorder_id and tax_assessor_id.
    This is the missing data Brett mentioned that could help with entity resolution.
    """
    
    query = """
    query RecorderV2Test {
      recorder_v2(limit: 5) {
        recorder_id
        tax_assessor_id
        document_type_code
        document_amount
        document_recorded_date
      }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {CHERRE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    
    print("\n" + "="*80)
    print("Testing recorder_v2 data availability (for entity resolution)...")
    print("="*80)
    
    try:
        response = requests.post(CHERRE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            print("❌ GraphQL Errors:")
            print(json.dumps(data["errors"], indent=2))
            return False
        
        if "data" in data and data["data"]["recorder_v2"]:
            records = data["data"]["recorder_v2"]
            print(f"✅ recorder_v2 data is available!")
            print(f"\nSample of {len(records)} records:")
            print(json.dumps(records, indent=2))
            
            # Check for nulls in key fields
            has_recorder_id = all(r.get("recorder_id") for r in records)
            has_tax_assessor_id = all(r.get("tax_assessor_id") for r in records)
            
            print(f"\n📊 Data Quality Check:")
            print(f"  - All records have recorder_id: {has_recorder_id}")
            print(f"  - All records have tax_assessor_id: {has_tax_assessor_id}")
            
            return True
        else:
            print("⚠️  No data returned (but no errors)")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


if __name__ == "__main__":
    print("="*80)
    print("CHERRE API TEST SUITE")
    print("="*80 + "\n")
    
    # Test 1: Basic API access
    test1 = test_simple_query()
    
    # Test 2: recorder_v2 availability (the missing data for entity resolution)
    test2 = test_recorder_v2_availability()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Basic API Access: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"recorder_v2 Data: {'✅ AVAILABLE' if test2 else '❌ UNAVAILABLE'}")
    print()

