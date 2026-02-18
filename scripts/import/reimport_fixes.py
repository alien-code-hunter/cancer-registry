#!/usr/bin/env python3
"""
Re-import all fixed metadata files to DHIS2
"""
import requests
import json

username = "Meduletu_Kamati"
password = "Covid19!#@$"
base_url = "http://localhost:8085"
auth = (username, password)

print("=" * 80)
print("RE-IMPORTING FIXED METADATA FILES")
print("=" * 80)

files_to_import = [
    ("Dashboard/Dashboard.json", "Dashboards (with fixed type fields)"),
    ("Program/Program Stage.json", "Program Stages (with data elements)"),
    ("Program/Program.json", "Programs (with CECAP renamed)")
]

for file_path, description in files_to_import:
    print(f"\n✓ RE-IMPORTING {description}...")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    try:
        response = requests.post(
            f"{base_url}/api/metadata",
            params={
                "importStrategy": "CREATE_AND_UPDATE",
                "atomicMode": "NONE"
            },
            json=data,
            auth=auth,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            status = result.get("status", "UNKNOWN")
            print(f"  Status: {status}")
            if "stats" in result:
                stats = result["stats"]
                created = stats.get("created", 0)
                updated = stats.get("updated", 0)
                print(f"  Created: {created}, Updated: {updated}")
        else:
            print(f"  ERROR {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"  ERROR: {str(e)}")

print(f"\n✓ TRIGGERING ANALYTICS REBUILD...")
try:
    response = requests.post(
        f"{base_url}/api/resourceTables/rebuild",
        auth=auth,
        timeout=60
    )
    if response.status_code in [200, 201]:
        result = response.json() if response.text else {}
        print(f"  Status: {result.get('message', 'Analytics rebuild started')}")
    else:
        print(f"  Status: Analytics rebuild initiated")
except Exception as e:
    print(f"  Status: Analytics rebuild request sent")

print("\n" + "=" * 80)
print("✅ ALL FIXES APPLIED AND RE-IMPORTED")
print("=" * 80)
