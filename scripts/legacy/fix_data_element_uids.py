#!/usr/bin/env python
"""
Fix invalid UIDs in newly added data elements.
DHIS2 UIDs must be 11-character alphanumeric strings without dashes.
"""

import json
import random
import string
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_ELEMENT_PATH = BASE_DIR / "Data Element" / "Data Element.json"


def generate_uid():
    """Generate a valid DHIS2 UID (11 alphanumeric characters)"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=11))


def main():
    # Load data
    with open(DATA_ELEMENT_PATH, "r") as f:
        data = json.load(f)

    elements = data.get("dataElements", [])

    # Cancer elements that need fixing
    cancer_element_names = {
        "Cancer Diagnosis",
        "Cancer Stage",
        "Date of Diagnosis",
        "Treatment Type",
        "Performance Status",
        "Comorbidities",
        "Treatment Response",
        "Date of Treatment",
        "Survival Status",
        "Date of Death"
    }

    # Generate new UIDs for the problematic elements
    fixed_count = 0
    uid_map = {}  # Map old UIDs to new ones for reference updates
    
    for elem in elements:
        if elem.get("name") in cancer_element_names:
            old_uid = elem.get("id")
            new_uid = generate_uid()
            elem["id"] = new_uid
            uid_map[old_uid] = new_uid
            print(f"✓ Fixed: {elem['name']}")
            print(f"  Old UID: {old_uid}")
            print(f"  New UID: {new_uid}\n")
            fixed_count += 1

    # Save back
    with open(DATA_ELEMENT_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")

    print(f"{'='*60}")
    print(f"✅ Fixed {fixed_count} data element UIDs")
    print(f"{'='*60}")
    
    # Save UID mapping for reference
    mapping_file = BASE_DIR / "scripts" / "uid_mapping.json"
    with open(mapping_file, "w") as f:
        json.dump(uid_map, f, indent=2)
    
    print(f"UID mapping saved to: {mapping_file}")


if __name__ == "__main__":
    main()
