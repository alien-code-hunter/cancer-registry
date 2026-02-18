#!/usr/bin/env python3
"""
Create program indicators for each cancer type.
Includes case counts, treatment outcomes, and survival metrics.
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]

def generate_uid():
    """Generate a DHIS2-compatible UID"""
    return str(uuid.uuid4())[:11]

# Load existing program indicators
pi_path = BASE_DIR / "Program" / "Program Indicator.json"
with open(pi_path) as f:
    pi_data = json.load(f)

existing_indicators = pi_data.get('programIndicators', [])
existing_names = {pi.get('name') for pi in existing_indicators}

# Load cancer programs to get their IDs
program_files = {
    'Bladder': BASE_DIR / "archive" / "programs" / "Bladder Cancer Program.json",
    'Breast': BASE_DIR / "archive" / "programs" / "Breast Cancer Program.json",
    # ... Add all other cancer programs
}

# Standard indicators to create for each cancer
INDICATOR_TEMPLATES = [
    {
        "name_pattern": "{cancer} - Total Cases",
        "short_name": "Total Cases",
        "description": "Total number of {cancer} cancer cases enrolled",
        "filter": "gender=M;gender=F"
    },
    {
        "name_pattern": "{cancer} - Cases by Gender",
        "short_name": "Cases by Gender",
        "description": "Number of {cancer} cancer cases stratified by gender",
        "filter": "gender=M;gender=F"
    },
    {
        "name_pattern": "{cancer} - Advanced Stage Cases",
        "short_name": "Stage III-IV",
        "description": "Number of {cancer} cancer cases at advanced stage (III-IV)",
        "filter": "stage=III;stage=IV"
    },
    {
        "name_pattern": "{cancer} - Treatment Completion Rate",
        "short_name": "Treatment Completion",
        "description": "Percentage of {cancer} cancer cases that completed planned treatment",
        "filter": None
    },
    {
        "name_pattern": "{cancer} - One-Year Survival",
        "short_name": "1-Year Survival",
        "description": "One-year survival rate for {cancer} cancer",
        "filter": None
    }
]

new_indicators = []
cancer_types = [
    'Bladder', 'Breast', 'Colorectal', 'Esophageal', 'Kaposi Sarcoma',
    'Kidney', 'Leukemia', 'Liver', 'Lung', 'Lymphoma', 'Oral Head Neck',
    'Ovarian', 'Pancreatic', 'Prostate', 'Skin Melanoma', 'Stomach',
    'Testicular', 'Thyroid'
]

for cancer in cancer_types:
    for template in INDICATOR_TEMPLATES:
        indicator_name = template['name_pattern'].format(cancer=cancer)
        
        if indicator_name not in existing_names:
            indicator = {
                "id": generate_uid(),
                "created": datetime.now().isoformat(),
                "lastUpdated": datetime.now().isoformat(),
                "name": indicator_name,
                "shortName": f"{cancer} - {template['short_name']}",
                "description": template['description'].format(cancer=cancer),
                "expression": f"d2:count('{generate_uid()}')",  # Placeholder expression
                "filter": template.get('filter'),
                "decimals": 0,
                "displayInForm": True,
                "analyticsPeriodBoundary": None,
                "sharing": {
                    "owner": "dhis2user",
                    "external": False,
                    "users": {},
                    "userGroups": {},
                    "public": "rw------"
                },
                "attributeValues": [],
                "translations": []
            }
            new_indicators.append(indicator)
            print(f"+ {cancer}: {template['short_name']}")

# Append to existing indicators
pi_data['programIndicators'].extend(new_indicators)

# Write back
with open(pi_path, 'w') as f:
    json.dump(pi_data, f, indent=2, ensure_ascii=True)

print(f"\n✓ Enhanced Program Indicators")
print(f"  Total indicators now: {len(pi_data['programIndicators'])}")
print(f"  New indicators added: {len(new_indicators)}")
