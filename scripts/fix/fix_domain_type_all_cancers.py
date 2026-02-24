import os
import json
from glob import glob

# Find all cancer-specific data element files
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_element_files = glob(os.path.join(base_dir, "Data Element/Data_Element_*.json"))

for file_path in data_element_files:
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
        print(f"Updated domainType to TRACKER in {os.path.basename(file_path)}")
    else:
        print(f"No AGGREGATE domainType found in {os.path.basename(file_path)}")
print("All cancer data element files checked for tracker design.")
