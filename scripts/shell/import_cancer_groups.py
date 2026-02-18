#!/usr/bin/env python3
"""Import Cancer Element and Indicator Groups to DHIS2."""

import json
import subprocess
import sys

DHIS2_URL = "http://localhost:8085"
USERNAME = "Meduletu_Kamati"
PASSWORD = "Covid19!#@$"

def import_groups(file_path, endpoint, group_key):
    """Import groups from JSON file to DHIS2."""
    print(f"\n📤 Importing {group_key.replace('_', ' ')} from {file_path}...")
    
    with open(file_path) as f:
        data = json.load(f)
    
    groups = data.get(group_key, [])
    print(f"   Found {len(groups)} {group_key.replace('_', ' ').lower()} to import")
    
    if not groups:
        print(f"   ⚠️  No groups found")
        return
    
    payload = {group_key: groups}
    
    # Use curl to POST
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{DHIS2_URL}/api/{endpoint}",
        "-u", f"{USERNAME}:{PASSWORD}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"   ❌ Failed to parse response: {result.stdout[:200]}")
        return
    
    # Parse response
    http_status = response.get("httpStatus", "UNKNOWN")
    if http_status == "OK":
        created = response.get("response", {}).get("created", 0)
        updated = response.get("response", {}).get("updated", 0)
        print(f"   ✅ {http_status}: {created} created, {updated} updated")
    else:
        print(f"   ❌ {http_status}")
        if "response" in response and "errorReports" in response["response"]:
            reports = response["response"]["errorReports"][:1]
            for report in reports:
                print(f"      Error: {report.get('message', 'Unknown error')}")

try:
    import_groups("Data Element/Data Element Group.json", "dataElementGroups", "dataElementGroups")
    import_groups("Options/Indicator Group.json", "indicatorGroups", "indicatorGroups")
    print("\n✅ Import process complete!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
