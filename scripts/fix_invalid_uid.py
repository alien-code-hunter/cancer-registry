#!/usr/bin/env python3
"""Fix the UID that starts with a number."""

import json
import random
import string
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_ELEMENT_PATH = BASE_DIR / "Data Element" / "Data Element.json"

def generate_valid_uid():
    """Generate a valid DHIS2 UID that starts with a letter"""
    chars = string.ascii_letters + string.digits
    first_char = random.choice(string.ascii_letters)
    remaining = ''.join(random.choices(chars, k=10))
    return first_char + remaining

# Load data
with open(DATA_ELEMENT_PATH) as f:
    data = json.load(f)

elements = data.get("dataElements", [])

# Find and fix the invalid UID
for elem in elements:
    if elem.get("id") == "5TAiG9FRUhG":
        old_uid = elem.get("id")
        new_uid = generate_valid_uid()
        elem["id"] = new_uid
        print(f"Fixed: {elem.get('name')}")
        print(f"  Old UID: {old_uid} (starts with number)")
        print(f"  New UID: {new_uid} (starts with letter)")
        break

# Save back
with open(DATA_ELEMENT_PATH, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=True)
    f.write("\n")

print("\n✅ Fixed invalid UID format")
