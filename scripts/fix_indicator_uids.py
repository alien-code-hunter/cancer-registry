#!/usr/bin/env python3
"""Fix invalid UIDs in Program Indicator.json."""

import json
import random
import string
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INDICATOR_PATH = BASE_DIR / "Program" / "Program Indicator.json"

def generate_valid_uid():
    """Generate a valid DHIS2 UID"""
    chars = string.ascii_letters + string.digits
    first_char = random.choice(string.ascii_letters)
    remaining = ''.join(random.choices(chars, k=10))
    return first_char + remaining

def is_valid_uid(uid):
    """Check if UID is valid"""
    if not uid or len(uid) != 11:
        return False
    if not uid[0].isalpha():
        return False
    if not all(c.isalnum() for c in uid):
        return False
    return True

# Load data
with open(INDICATOR_PATH) as f:
    data = json.load(f)

indicators = data.get("programIndicators", [])
fixed_count = 0

# Fix indicator UIDs
for i, indicator in enumerate(indicators):
    uid = indicator.get("id")
    if uid and not is_valid_uid(uid):
        new_uid = generate_valid_uid()
        indicator["id"] = new_uid
        fixed_count += 1
        if fixed_count <= 5:  # Show first 5
            print(f"Indicator {indicator.get('name')}: {uid} -> {new_uid}")

# Save
with open(INDICATOR_PATH, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=True)
    f.write("\n")

print(f"\n✅ Fixed {fixed_count} invalid UIDs in Program Indicator.json")
