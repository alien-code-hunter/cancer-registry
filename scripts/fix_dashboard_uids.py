#!/usr/bin/env python3
"""Fix invalid UIDs in Dashboard.json - ensure all start with letters and are 11 chars."""

import json
import random
import string
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = BASE_DIR / "Dashboard" / "Dashboard.json"

def generate_valid_uid():
    """Generate a valid DHIS2 UID (11 chars, starts with letter)"""
    chars = string.ascii_letters + string.digits
    first_char = random.choice(string.ascii_letters)
    remaining = ''.join(random.choices(chars, k=10))
    return first_char + remaining

def is_valid_uid(uid):
    """Check if UID is valid (11 chars, starts with letter, alphanumeric)"""
    if not uid or len(uid) != 11:
        return False
    if not uid[0].isalpha():
        return False
    if not all(c.isalnum() for c in uid):
        return False
    return True

# Load data
with open(DASHBOARD_PATH) as f:
    data = json.load(f)

dashboards = data.get("dashboards", [])
fixed_count = 0
uid_map = {}

# Fix dashboard UIDs
for i, dashboard in enumerate(dashboards):
    uid = dashboard.get("id")
    if uid and not is_valid_uid(uid):
        new_uid = generate_valid_uid()
        uid_map[uid] = new_uid
        dashboard["id"] = new_uid
        print(f"Dashboard {i+1}: {dashboard.get('name')}")
        print(f"  {uid} -> {new_uid}")
        fixed_count += 1
    
    # Fix dashboard items' UIDs
    dashboard_items = dashboard.get("dashboardItems", [])
    for j, item in enumerate(dashboard_items):
        item_uid = item.get("id")
        if item_uid and not is_valid_uid(item_uid):
            new_uid = generate_valid_uid()
            uid_map[item_uid] = new_uid
            item["id"] = new_uid
            fixed_count += 1

# Save
with open(DASHBOARD_PATH, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=True)
    f.write("\n")

# Save mapping
mapping_file = BASE_DIR / "scripts" / "dashboard_uid_mapping.json"
with open(mapping_file, "w") as f:
    json.dump(uid_map, f, indent=2)

print(f"\n✅ Fixed {fixed_count} invalid UIDs in Dashboard.json")
print(f"Mapping saved to: {mapping_file}")
