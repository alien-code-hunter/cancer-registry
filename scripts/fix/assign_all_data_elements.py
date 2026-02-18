#!/usr/bin/env python3
"""
Fast Data Element Assignment - Optimized Version
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# Load all data once
stage_path = BASE_DIR / "Program" / "Program Stage.json"
de_path = BASE_DIR / "Data Element" / "Data Element.json"

with open(stage_path) as f:
    stage_data = json.load(f)
with open(de_path) as f:
    de_data = json.load(f)

# Get all data elements
all_elements = [de.get('id') for de in de_data.get('dataElements', [])]

# Assign ALL data elements to ALL stages (simplified approach)
# This makes sense for a cancer registry where all stages may need all elements
stages = stage_data.get('programStages', [])
updated = 0

for stage in stages:
    existing = stage.get('programStageDataElements', []) or []
    existing_ids = {item.get('dataElement', {}).get('id') for item in existing}
    
    # Add missing elements
    sort_order = len(existing) + 1
    for elem_id in all_elements:
        if elem_id not in existing_ids:
            existing.append({
                'dataElement': {'id': elem_id},
                'compulsory': False,
                'allowProvidedElsewhere': False,
                'allowFutureDate': False,
                'sortOrder': sort_order
            })
            sort_order += 1
    
    if existing:
        stage['programStageDataElements'] = existing
        updated += 1

# Save
with open(stage_path, 'w') as f:
    json.dump(stage_data, f, indent=2, ensure_ascii=True)
    f.write('\n')

print(f"✅ Assigned {len(all_elements)} data elements to {updated} program stages")
