#!/usr/bin/env python3
"""
Enhance data elements for cancer registry.
Adds missing critical elements like Gender, Diagnosis, and Stage.
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]

def generate_uid():
    """Generate a DHIS2-compatible UID"""
    import uuid
    return str(uuid.uuid4())[:11]

# Load existing data elements
de_path = BASE_DIR / "Data Element" / "Data Element.json"
with open(de_path) as f:
    de_data = json.load(f)

existing_elements = de_data.get('dataElements', [])
existing_names = {de.get('name') for de in existing_elements}

# Critical data elements for cancer registry
CRITICAL_ELEMENTS = [
    {
        "name": "Cancer Diagnosis",
        "short_name": "Cancer Diagnosis",
        "description": "Primary cancer diagnosis (ICD-10)",
        "value_type": "TEXT",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    },
    {
        "name": "Cancer Stage",
        "short_name": "Stage",
        "description": "TNM Stage of cancer (I, II, III, IV)",
        "value_type": "TEXT",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    },
    {
        "name": "Date of Diagnosis",
        "short_name": "Diagnosis Date",
        "description": "Date when cancer diagnosis was confirmed",
        "value_type": "DATE",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    },
    {
        "name": "Treatment Type",
        "short_name": "Treatment",
        "description": "Primary treatment modality (Surgery, Chemotherapy, Radiation, Immunotherapy)",
        "value_type": "TEXT",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    },
    {
        "name": "Performance Status",
        "short_name": "ECOG Status",
        "description": "ECOG performance status (0-4)",
        "value_type": "INTEGER_ZERO_OR_POSITIVE",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    },
    {
        "name": "Comorbidities",
        "short_name": "Comorbidities",
        "description": "Presence of comorbid conditions affecting treatment",
        "value_type": "TEXT",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    },
    {
        "name": "Treatment Response",
        "short_name": "Response",
        "description": "Treatment response (CR, PR, SD, PD)",
        "value_type": "TEXT",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    },
    {
        "name": "Date of Treatment",
        "short_name": "Treatment Date",
        "description": "Date treatment was initiated",
        "value_type": "DATE",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    },
    {
        "name": "Survival Status",
        "short_name": "Survival",
        "description": "Patient survival status (Alive, Deceased, Lost to follow-up)",
        "value_type": "TEXT",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    },
    {
        "name": "Date of Death",
        "short_name": "Death Date",
        "description": "Date of death if applicable",
        "value_type": "DATE",
        "aggregation_level": 0,
        "domain_type": "TRACKER"
    }
]

# Check which elements are missing
new_elements = []
for elem_spec in CRITICAL_ELEMENTS:
    if elem_spec['name'] not in existing_names:
        element = {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": elem_spec['name'],
            "shortName": elem_spec['short_name'],
            "description": elem_spec['description'],
            "valueType": elem_spec['value_type'],
            "aggregationType": "NONE",
            "domainType": elem_spec['domain_type'],
            "displayInReports": True,
            "zeroIsSignificant": False,
            "color": "#2E7D32",
            "icon": "dhis2-icon-functions",
            "optionSet": None,
            "commentOptionSet": None,
            "attributeValues": [],
            "sharing": {
                "owner": "dhis2user",
                "external": False,
                "users": {},
                "userGroups": {},
                "public": "rw------"
            },
            "translations": [],
            "formName": elem_spec['name']
        }
        new_elements.append(element)
        print(f"+ Added: {elem_spec['name']}")
    else:
        print(f"✓ Already exists: {elem_spec['name']}")

# Append new elements to existing data
de_data['dataElements'].extend(new_elements)

# Write back with all elements
with open(de_path, 'w') as f:
    json.dump(de_data, f, indent=2, ensure_ascii=True)

print(f"\n✓ Enhanced Data Element file")
print(f"  Total elements now: {len(de_data['dataElements'])}")
print(f"  New elements added: {len(new_elements)}")
