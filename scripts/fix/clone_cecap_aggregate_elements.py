#!/usr/bin/env python3
"""
Clone existing aggregate data elements (CECAP-style) for all other cancers,
so they appear in Data Visualizer like the cervical program.
"""
import json
import random
import string
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DE_PATH = BASE_DIR / "Data Element" / "Data Element.json"
DS_PATH = BASE_DIR / "Data Set" / "Data Set.json"

CANCERS = [
    "Bladder",
    "Breast",
    "Colorectal",
    "Esophageal",
    "Kaposi Sarcoma",
    "Kidney",
    "Leukemia",
    "Liver",
    "Lung",
    "Lymphoma",
    "Oral Head Neck",
    "Ovarian",
    "Pancreatic",
    "Prostate",
    "Skin Melanoma",
    "Stomach",
    "Testicular",
    "Thyroid",
]


def generate_uid():
    chars = string.ascii_letters + string.digits
    first = random.choice(string.ascii_letters)
    rest = "".join(random.choice(chars) for _ in range(10))
    return first + rest


def main():
    with open(DE_PATH) as f:
        de_data = json.load(f)

    data_elements = de_data.get("dataElements", [])
    existing_names = {de.get("name") for de in data_elements}
    existing_ids = {de.get("id") for de in data_elements}

    base_aggs = [de for de in data_elements if de.get("domainType") == "AGGREGATE"]
    if not base_aggs:
        print("No aggregate data elements found. Nothing to clone.")
        return

    now = datetime.now().isoformat()
    created = 0

    for cancer in CANCERS:
        for base in base_aggs:
            base_name = base.get("name", "")
            if not base_name:
                continue
            new_name = f"{cancer} - {base_name}"
            if new_name in existing_names:
                continue

            new_id = generate_uid()
            while new_id in existing_ids:
                new_id = generate_uid()

            clone = json.loads(json.dumps(base))
            clone["id"] = new_id
            clone["name"] = new_name
            clone["shortName"] = new_name
            clone["formName"] = new_name
            clone["created"] = now
            clone["lastUpdated"] = now

            data_elements.append(clone)
            existing_names.add(new_name)
            existing_ids.add(new_id)
            created += 1

    de_data["dataElements"] = data_elements
    with open(DE_PATH, "w") as f:
        json.dump(de_data, f, indent=2, ensure_ascii=True)
        f.write("\n")

    # Update dataset to include the new aggregate elements
    with open(DS_PATH) as f:
        ds_data = json.load(f)

    data_sets = ds_data.get("dataSets", [])
    if not data_sets:
        print("No data sets found; skipped dataset updates.")
        return

    ds = data_sets[0]
    ds_id = ds.get("id")
    existing_ds_ids = {e.get("dataElement", {}).get("id") for e in ds.get("dataSetElements", [])}

    new_ds_elements = []
    for de in data_elements:
        if de.get("domainType") != "AGGREGATE":
            continue
        de_id = de.get("id")
        if de_id in existing_ds_ids:
            continue
        new_ds_elements.append({
            "dataSet": {"id": ds_id},
            "dataElement": {"id": de_id},
        })

    if new_ds_elements:
        ds.setdefault("dataSetElements", []).extend(new_ds_elements)
        with open(DS_PATH, "w") as f:
            json.dump(ds_data, f, indent=2, ensure_ascii=True)
            f.write("\n")

    print(f"Created {created} aggregate data elements.")
    print(f"Added {len(new_ds_elements)} elements to dataset '{ds.get('name')}'.")


if __name__ == "__main__":
    main()
