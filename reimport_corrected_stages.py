#!/usr/bin/env python3
"""
Re-import corrected Program Stages (AGGREGATE elements removed)
"""
import json
import urllib.request
import base64

BASE_URL = "http://localhost:8085"
USERNAME = "Meduletu_Kamati"
PASSWORD = "Covid19!#@$"

auth_string = f"{USERNAME}:{PASSWORD}".encode('utf-8')
auth_b64 = base64.b64encode(auth_string).decode('ascii')
auth_header = f"Basic {auth_b64}"

print("=" * 80)
print("RE-IMPORTING CORRECTED PROGRAM STAGES")
print("=" * 80)

print("\n📤 Importing Program Stages (AGGREGATE elements removed)...")

with open('Program/Program Stage.json', 'r') as f:
    data = json.load(f)

json_bytes = json.dumps(data).encode('utf-8')

req = urllib.request.Request(
    f"{BASE_URL}/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE",
    data=json_bytes,
    headers={
        'Content-Type': 'application/json',
        'Authorization': auth_header
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        status = result.get('status', 'UNKNOWN')
        stats = result.get('stats', {})
        created = stats.get('created', 0)
        updated = stats.get('updated', 0)
        
        print(f"   ✅ Status: {status}")
        print(f"      Created: {created}, Updated: {updated}")
        
except Exception as e:
    print(f"   ❌ ERROR: {str(e)[:150]}")

print("\n" + "=" * 80)
print("✅ PROGRAM STAGES RE-IMPORTED (FIXED)")
print("=" * 80)
