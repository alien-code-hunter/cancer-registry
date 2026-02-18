#!/usr/bin/env python
"""
Update references to old UIDs in Dashboard and Program Indicator files.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
UID_MAPPING_FILE = BASE_DIR / "scripts" / "uid_mapping.json"
DASHBOARD_PATH = BASE_DIR / "Dashboard" / "Dashboard.json"
INDICATOR_PATH = BASE_DIR / "Program" / "Program Indicator.json"


def update_file_with_uid_map(file_path, uid_map):
    """Update a file by replacing old UIDs with new ones"""
    with open(file_path, "r") as f:
        content = f.read()
    
    original_content = content
    
    # Replace all old UIDs with new ones
    for old_uid, new_uid in uid_map.items():
        content = content.replace(old_uid, new_uid)
    
    # If content changed, save it
    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        return True
    return False


def main():
    # Load UID mapping
    with open(UID_MAPPING_FILE, "r") as f:
        uid_map = json.load(f)
    
    print("UID Mapping loaded:")
    print("=" * 60)
    for old_uid, new_uid in uid_map.items():
        print(f"{old_uid} -> {new_uid}")
    
    print("\n" + "=" * 60)
    
    # Update Dashboard.json
    print("\nUpdating Dashboard.json...")
    if update_file_with_uid_map(DASHBOARD_PATH, uid_map):
        print("✓ Updated Dashboard.json with new UIDs")
    else:
        print("✓ No old UIDs found in Dashboard.json")
    
    # Update Program Indicator.json
    print("\nUpdating Program Indicator.json...")
    if update_file_with_uid_map(INDICATOR_PATH, uid_map):
        print("✓ Updated Program Indicator.json with new UIDs")
    else:
        print("✓ No old UIDs found in Program Indicator.json")
    
    print("\n" + "=" * 60)
    print("✅ All files updated successfully!")


if __name__ == "__main__":
    main()
