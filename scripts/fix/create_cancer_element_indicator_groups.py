#!/usr/bin/env python3
"""
Create Data Element Groups and Indicator Groups for each cancer type.

This script generates groupings for cancer-specific aggregate data elements
and indicators to organize them logically in DHIS2 dashboards and reports.

- Creates 18 Data Element Groups (one per cancer type)
- Creates 18 Indicator Groups (one per cancer type)
- Each group contains relevant cancer-specific elements/indicators

Outputs:
  - Data Element/Data Element Group.json (updated)
  - Options/Indicator Group.json (updated)
"""

import json
import uuid
import random
import string
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[2]

# Cancer types list (18 cancers, alphabetically ordered)
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

CERVICAL = "Cervical"  # Special case: Cervical cancer (CECAP)

# DHIS2 default settings
DEFAULT_USER_ID = "M5zQapPyTZI"
DEFAULT_USERNAME = "admin"
DEFAULT_USER_NAME = "admin admin"


def generate_uid():
    """Generate a DHIS2-compatible UID (11 char alphanumeric)."""
    # Use mix of letters and numbers to ensure valid DHIS2 UID
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=11))


def load_data_elements():
    """Load all data elements to find cancer-specific ones."""
    de_file = REPO_ROOT / "Data Element" / "Data Element.json"
    with open(de_file) as f:
        data = json.load(f)
    return data["dataElements"]


def load_indicators():
    """Load all indicators to find cancer-specific ones."""
    ind_file = REPO_ROOT / "Options" / "Indicator.json"
    with open(ind_file) as f:
        data = json.load(f)
    return data.get("indicators", [])


def get_cancer_elements(data_elements, cancer_name):
    """Get all data elements for a specific cancer type."""
    prefix = f"{cancer_name} - "
    return [elem for elem in data_elements if elem["name"].startswith(prefix)]


def get_cancer_indicators(indicators, cancer_name):
    """Get all indicators for a specific cancer type."""
    prefix = f"{cancer_name} "
    return [ind for ind in indicators if ind["name"].startswith(prefix)]


def create_data_element_group(cancer_name, data_element_ids):
    """Create a Data Element Group for a cancer type."""
    return {
        "id": generate_uid(),
        "code": f"DEG_{cancer_name.replace(' ', '_').upper()}",
        "name": f"{cancer_name} Data Elements",
        "shortName": f"{cancer_name} DE Group",
        "description": f"Aggregate data elements for {cancer_name} cancer screening and treatment",
        "created": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "lastUpdated": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "createdBy": {
            "id": DEFAULT_USER_ID,
            "code": DEFAULT_USERNAME,
            "name": DEFAULT_USER_NAME,
            "displayName": DEFAULT_USER_NAME,
            "username": DEFAULT_USERNAME,
        },
        "lastUpdatedBy": {
            "id": DEFAULT_USER_ID,
            "code": DEFAULT_USERNAME,
            "name": DEFAULT_USER_NAME,
            "displayName": DEFAULT_USER_NAME,
            "username": DEFAULT_USERNAME,
        },
        "sharing": {
            "owner": DEFAULT_USER_ID,
            "external": False,
            "users": {},
            "userGroups": {},
            "public": "rw------",
        },
        "dataElements": [{"id": elem_id} for elem_id in data_element_ids],
    }


def create_indicator_group(cancer_name, indicator_ids):
    """Create an Indicator Group for a cancer type."""
    return {
        "id": generate_uid(),
        "code": f"IGP_{cancer_name.replace(' ', '_').upper()}",
        "name": f"{cancer_name} Indicators",
        "shortName": f"{cancer_name} Indicators",
        "description": f"Aggregate indicators for {cancer_name} cancer screening and treatment",
        "created": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "lastUpdated": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "createdBy": {
            "id": DEFAULT_USER_ID,
            "code": DEFAULT_USERNAME,
            "name": DEFAULT_USER_NAME,
            "displayName": DEFAULT_USER_NAME,
            "username": DEFAULT_USERNAME,
        },
        "lastUpdatedBy": {
            "id": DEFAULT_USER_ID,
            "code": DEFAULT_USERNAME,
            "name": DEFAULT_USER_NAME,
            "displayName": DEFAULT_USER_NAME,
            "username": DEFAULT_USERNAME,
        },
        "sharing": {
            "owner": DEFAULT_USER_ID,
            "external": False,
            "users": {},
            "userGroups": {},
            "public": "rw------",
        },
        "indicators": [{"id": ind_id} for ind_id in indicator_ids],
    }


def main():
    """Generate and save cancer element/indicator groups."""
    print("Loading metadata...")
    data_elements = load_data_elements()
    indicators = load_indicators()

    data_element_groups = []
    indicator_groups = []
    group_summary = []

    print(f"\nProcessing {len(CANCERS)} cancer types...\n")

    for cancer in CANCERS:
        # Get cancer-specific elements and indicators
        cancer_elems = get_cancer_elements(data_elements, cancer)
        cancer_inds = get_cancer_indicators(indicators, cancer)

        if not cancer_elems and not cancer_inds:
            print(f"⚠️  {cancer}: No elements or indicators found")
            continue

        # Create groups
        line = f"{cancer:20s}: "
        if cancer_elems:
            elem_ids = [elem["id"] for elem in cancer_elems]
            deg = create_data_element_group(cancer, elem_ids)
            data_element_groups.append(deg)
            line += f"{len(cancer_elems):2d} data elements"
        else:
            line += "0 data elements"

        if cancer_inds:
            ind_ids = [ind["id"] for ind in cancer_inds]
            igp = create_indicator_group(cancer, ind_ids)
            indicator_groups.append(igp)
            line += f", {len(cancer_inds)} indicators ✓"
        else:
            line += ", 0 indicators ✓"

        group_summary.append(line)

    # Print summary
    print("Cancer Group Summary:")
    print("-" * 60)
    for line in group_summary:
        print(line)

    # Save Data Element Groups
    deg_file = REPO_ROOT / "Data Element" / "Data Element Group.json"
    deg_output = {
        "system": {
            "id": "039b6994-a3e7-4531-967d-d5db7fceb5eb",
            "rev": "dfd7f48",
            "version": "2.40.5",
            "date": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        },
        "dataElementGroups": data_element_groups,
    }
    with open(deg_file, "w") as f:
        json.dump(deg_output, f, indent=2)
    print(f"\n✅ Created {len(data_element_groups)} Data Element Groups")
    print(f"   Saved to: Data Element/Data Element Group.json")

    # Save Indicator Groups
    igp_file = REPO_ROOT / "Options" / "Indicator Group.json"
    igp_output = {
        "system": {
            "id": "039b6994-a3e7-4531-967d-d5db7fceb5eb",
            "rev": "dfd7f48",
            "version": "2.40.5",
            "date": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        },
        "indicatorGroups": indicator_groups,
    }
    with open(igp_file, "w") as f:
        json.dump(igp_output, f, indent=2)
    print(f"✅ Created {len(indicator_groups)} Indicator Groups")
    print(f"   Saved to: Options/Indicator Group.json")

    # Generate summary report
    report_file = REPO_ROOT / "artifacts" / "reports" / "CANCER_GROUPS_SUMMARY.txt"
    with open(report_file, "w") as f:
        f.write("Cancer Element & Indicator Groups Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Data Element Groups: {len(data_element_groups)}\n")
        f.write(f"Total Indicator Groups: {len(indicator_groups)}\n\n")
        f.write("Breakdown by Cancer Type:\n")
        f.write("-" * 60 + "\n")
        for cancer in CANCERS:
            cancer_elems = get_cancer_elements(data_elements, cancer)
            cancer_inds = get_cancer_indicators(indicators, cancer)
            f.write(f"\n{cancer}:\n")
            f.write(f"  Data Elements: {len(cancer_elems)}\n")
            f.write(f"  Indicators: {len(cancer_inds)}\n")
            if cancer_elems:
                f.write(f"  Element IDs: {', '.join([e['id'] for e in cancer_elems[:3]])}")
                if len(cancer_elems) > 3:
                    f.write(f", ... ({len(cancer_elems) - 3} more)")
                f.write("\n")
            if cancer_inds:
                f.write(f"  Indicator IDs: {', '.join([i['id'] for i in cancer_inds[:3]])}")
                if len(cancer_inds) > 3:
                    f.write(f", ... ({len(cancer_inds) - 3} more)")
                f.write("\n")

    print(f"✅ Generated summary report: artifacts/reports/CANCER_GROUPS_SUMMARY.txt")


if __name__ == "__main__":
    main()
