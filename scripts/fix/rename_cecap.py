#!/usr/bin/env python3
"""
Rename CECAP to Cervical Cancer Program
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# 1. Rename in Program.json
prog_path = BASE_DIR / "Program" / "Program.json"
with open(prog_path) as f:
    data = json.load(f)

for prog in data.get('programs', []):
    if 'CECAP' in prog.get('name', ''):
        print(f"Renaming: {prog.get('name')} → Cervical Cancer Program")
        prog['name'] = 'Cervical Cancer Program'
        prog['shortName'] = 'CCP'
        prog['description'] = 'Cervical cancer screening, diagnosis, treatment, and follow-up program'

with open(prog_path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=True)
    f.write('\n')

# 2. Rename in Program Stage.json
stage_path = BASE_DIR / "Program" / "Program Stage.json"
with open(stage_path) as f:
    stage_data = json.load(f)

renamed_count = 0
for stage in stage_data.get('programStages', []):
    name = stage.get('name', '')
    if 'CECAP' in name:
        old_name = name
        stage['name'] = name.replace('CECAP', 'Cervical Cancer')
        print(f"Renamed stage: {old_name} → {stage['name']}")
        renamed_count += 1

with open(stage_path, 'w') as f:
    json.dump(stage_data, f, indent=2, ensure_ascii=True)
    f.write('\n')

print(f"\n✅ Renamed CECAP to Cervical Cancer Program ({renamed_count} stages updated)")
