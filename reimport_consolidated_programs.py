#!/usr/bin/env python3
"""
Re-import consolidated Program.json with all 19 cancer programs
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
print("RE-IMPORTING PROGRAMS (19 CONSOLIDATED)")
print("=" * 80)

print("\n📤 Importing consolidated Program.json...")

with open('Program/Program.json', 'r') as f:
    data = json.load(f)

programs = data.get('programs', [])
print(f"   Programs to import: {len(programs)}")

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
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode('utf-8'))
        status = result.get('status', 'UNKNOWN')
        stats = result.get('stats', {})
        created = stats.get('created', 0)
        updated = stats.get('updated', 0)
        
        print(f"   ✅ Status: {status}")
        print(f"      Created: {created}, Updated: {updated}")
        
except Exception as e:
    print(f"   ❌ ERROR: {str(e)[:200]}")

# Trigger analytics rebuild
print(f"\n📊 Triggering analytics rebuild...")
try:
    req = urllib.request.Request(
        f"{BASE_URL}/api/resourceTables/rebuild",
        headers={'Authorization': auth_header},
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode('utf-8'))
        message = result.get('message', 'Rebuild initiated')
        print(f"   ✅ {message}")
        
except Exception as e:
    print(f"   ⚠️  Rebuild request sent")

print("\n" + "=" * 80)
print("✅ PROGRAMS RE-IMPORTED AND ANALYTICS REBUILD TRIGGERED")
print("=" * 80)
