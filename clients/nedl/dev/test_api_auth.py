#!/usr/bin/env python3
"""Quick test of Cherre API authentication"""
import requests
from config import CHERRE_API_KEY, CHERRE_API_URL

print(f"Testing Cherre API authentication...")
print(f"API URL: {CHERRE_API_URL}")
print(f"API Key (first 20 chars): {CHERRE_API_KEY[:20]}...")

query = """
query {
    recorder_v2(limit: 1) {
        recorder_id
    }
}
"""

headers = {
    "Authorization": f"Basic {CHERRE_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(CHERRE_API_URL, headers=headers, json={"query": query})

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    print("\n✅ Authentication successful!")
else:
    print("\n❌ Authentication failed!")
    print("\nPossible issues:")
    print("1. API key expired")
    print("2. API key invalid")
    print("3. IP address not whitelisted")
    print("4. Cherre service issue")

