import os
import json
from glob import glob

# Path to all data element files
DATA_ELEMENT_FILES = [
    "Data Element/Data Element.json",
    "Data Element/Data_Element_Generic.json"
]

# Find all data element files in the workspace
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel_path in DATA_ELEMENT_FILES:
    file_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(file_path):
        continue
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    changed = False
    for de in data.get("dataElements", []):
        if de.get("domainType") == "AGGREGATE":
            de["domainType"] = "TRACKER"
            changed = True
    if changed:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Updated domainType to TRACKER in {rel_path}")
    else:
        print(f"No AGGREGATE domainType found in {rel_path}")
print("DomainType fix complete.")
