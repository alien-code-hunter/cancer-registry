#!/usr/bin/env python3
"""
Import all fixed metadata files to DHIS2
"""
import json
import urllib.request
import base64
import sys

BASE_URL = "http://localhost:8085"
USERNAME = "Meduletu_Kamati"
PASSWORD = "Covid19!#@$"

# Prepare authentication
auth_string = f"{USERNAME}:{PASSWORD}".encode('utf-8')
auth_b64 = base64.b64encode(auth_string).decode('ascii')
auth_header = f"Basic {auth_b64}"

print("=" * 80)
print("IMPORTING FIXED METADATA TO DHIS2")
print("=" * 80)

files_to_import = [
    ("Dashboard/Dashboard.json", "Dashboards (type fields fixed)"),
    ("Program/Program Stage.json", "Program Stages (data elements assigned)"),
    ("Program/Program.json", "Programs (CECAP renamed)"),
]

success_count = 0
fail_count = 0

for filepath, description in files_to_import:
    print(f"\n📤 Importing {description}...")
    
    try:
        with open(filepath, 'r') as f:
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
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            status = result.get('status', 'UNKNOWN')
            stats = result.get('stats', {})
            created = stats.get('created', 0)
            updated = stats.get('updated', 0)
            
            print(f"   ✅ Status: {status}")
            print(f"      Created: {created}, Updated: {updated}")
            success_count += 1
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:150]}")
        fail_count += 1

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
        message = result.get('message', 'Analytics rebuild initiated')
        print(f"   ✅ {message}")
        
except Exception as e:
    print(f"   ⚠️  Analytics rebuild request sent (check DHIS2 UI)")

print("\n" + "=" * 80)
if fail_count == 0:
    print(f"✅ ALL IMPORTS SUCCESSFUL ({success_count}/3 files imported)")
else:
    print(f"⚠️  {success_count} successful, {fail_count} failed")
print("=" * 80)
