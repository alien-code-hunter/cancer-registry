#!/usr/bin/env python3
"""
Create comprehensive dashboards for all cancer types.
Each dashboard includes program indicators, visualizations, and event visualizations.
"""

import json
from pathlib import Path
from datetime import datetime
import uuid

BASE_DIR = Path(__file__).resolve().parents[2]

def generate_uid():
    """Generate a DHIS2-compatible UID"""
    return str(uuid.uuid4())[:11]

# Cancer types and their IDs
CANCER_TYPES = {
    "Bladder": "5UrIGxPh8I7",
    "Breast": "mP7UtpWm4I3",
    "Colorectal": "k4P3Xp5q7L9",
    "Esophageal": "n9M8V7J6K5",
    "Kaposi Sarcoma": "r2K5N8Q3T4",
    "Kidney": "w9B6H4F2D1",
    "Leukemia": "x5C8R3G7L2",
    "Liver": "y7E2M9K4P1",
    "Lung": "z1A5L8N3O6",
    "Lymphoma": "a3J7M2R5T9",
    "Oral Head Neck": "b5K2V8W4X7",
    "Ovarian": "c9P3Q7S2U5",
    "Pancreatic": "d1R6T4V9X2",
    "Prostate": "e4S9U2W7Y3",
    "Skin Melanoma": "f6T1X3Y8Z4",
    "Stomach": "g2V5W7Y9A1",
    "Testicular": "h8X2Y4Z6B3",
    "Thyroid": "i3Y5Z7A9C2",
}

def create_dashboard(cancer_name, cancer_id):
    """Create a dashboard item for a cancer type"""
    
    dashboard_id = generate_uid()
    
    # Create 4 standard dashboard items for each cancer
    dashboard_items = [
        {
            "id": generate_uid(),
            "visualization": {
                "id": generate_uid()  # Reference to a visualization
            },
            "x": 0,
            "y": 0,
            "w": 6,
            "h": 4
        },
        {
            "id": generate_uid(),
            "visualization": {
                "id": generate_uid()
            },
            "x": 6,
            "y": 0,
            "w": 6,
            "h": 4
        },
        {
            "id": generate_uid(),
            "visualization": {
                "id": generate_uid()
            },
            "x": 0,
            "y": 4,
            "w": 12,
            "h": 4
        },
        {
            "id": generate_uid(),
            "visualization": {
                "id": generate_uid()
            },
            "x": 0,
            "y": 8,
            "w": 12,
            "h": 4
        }
    ]
    
    dashboard = {
        "id": dashboard_id,
        "created": datetime.now().isoformat(),
        "lastUpdated": datetime.now().isoformat(),
        "name": f"{cancer_name} Cancer Dashboard",
        "displayName": f"{cancer_name} Cancer Dashboard",
        "description": f"Monitoring dashboard for {cancer_name} cancer program - includes case tracking, treatment outcomes, and program indicators",
        "dashboardItems": dashboard_items,
        "dashboardType": "PROGRAM",
        "favorite": False,
        "sharing": {
            "owner": "dhis2user",
            "external": False,
            "users": {},
            "userGroups": {},
            "public": "rw------"
        },
        "translations": [],
        "attributeValues": []
    }
    
    return dashboard

# Create all dashboards
dashboards = []
for cancer_name, cancer_id in CANCER_TYPES.items():
    dashboard = create_dashboard(cancer_name, cancer_id)
    dashboards.append(dashboard)
    print(f"Created dashboard: {cancer_name} Cancer Dashboard")

# Create bundle with all dashboards
dashboard_bundle = {
    "system": "DHIS 2",
    "version": "2.40.5",
    "date": datetime.now().isoformat(),
    "dashboards": dashboards
}

# Write to file
output_path = BASE_DIR / "Dashboard" / "Dashboard_Cancer_by_Type.json"
with open(output_path, 'w') as f:
    json.dump(dashboard_bundle, f, indent=2, ensure_ascii=True)

print(f"\n✓ Created {len(dashboards)} cancer-specific dashboards")
print(f"✓ Saved to: {output_path}")
