#!/usr/bin/env python3
"""
1. Rename and improve program stages to real-world cancer clinical workflow.
   Standard 8-stage cancer tracking flow used across all 18 cancer types.
"""

import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parents[1]
STAGE_PATH = BASE_DIR / "Program" / "Program Stage.json"
PROGRAM_PATH = BASE_DIR / "Program" / "Program.json"

# Real-world clinical cancer workflow stages
# Since each program has 4 stages, we'll use the first 4 of the standard workflow
STANDARD_CANCER_STAGES = [
    {
        "name": "1. Initial Assessment & Diagnostics",
        "description": "Patient presentation and initial clinical evaluation - chief complaint, risk factors, symptoms, performance status",
        "sortOrder": 1
    },
    {
        "name": "2. Staging & Treatment Planning",
        "description": "TNM staging, risk assessment, treatment plan - surgery, chemotherapy, radiation, immunotherapy options",
        "sortOrder": 2
    },
    {
        "name": "3. Active Treatment",
        "description": "Treatment execution - compliance monitoring, toxicity assessment, treatment adjustments",
        "sortOrder": 3
    },
    {
        "name": "4. Follow-up & Outcomes",
        "description": "Long-term monitoring and final outcomes - response assessment, surveillance, recurrence, survival",
        "sortOrder": 4
    }
]

def main():
    # Load data
    with open(STAGE_PATH) as f:
        stages_data = json.load(f)
    
    with open(PROGRAM_PATH) as f:
        programs_data = json.load(f)
    
    stages = stages_data.get("programStages", [])
    programs = {p.get("id"): p.get("name") for p in programs_data.get("programs", [])}
    
    # Group existing stages by program 
    stages_by_program = defaultdict(list)
    for stage in stages:
        prog_id = stage.get("program", {}).get("id")
        if prog_id:
            stages_by_program[prog_id].append(stage)
    
    # Rename stages for each program to standard clinical workflow
    renamed_count = 0
    for prog_id, prog_name in programs.items():
        program_stages = stages_by_program.get(prog_id, [])
        
        if not program_stages:
            continue
        
        # Sort existing stages by sortOrder
        program_stages_sorted = sorted(program_stages, key=lambda x: x.get("sortOrder", 999))
        
        # Rename up to 4 stages with standard cancer workflow names
        for i, standard_stage in enumerate(STANDARD_CANCER_STAGES):
            if i < len(program_stages_sorted):
                old_name = program_stages_sorted[i].get("name")
                # Only update if it looks like a generic name (ends with "Stage")
                if old_name.endswith("Stage") or old_name.startswith("Stage"):
                    program_stages_sorted[i]["name"] = standard_stage["name"]
                    program_stages_sorted[i]["description"] = standard_stage["description"]
                    program_stages_sorted[i]["sortOrder"] = standard_stage["sortOrder"]
                    print(f"✓ {prog_name}:")
                    print(f"    {old_name} → {standard_stage['name']}")
                    renamed_count += 1
    
    # Save
    with open(STAGE_PATH, "w") as f:
        json.dump(stages_data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"\n{'='*80}")
    print(f"✅ Renamed {renamed_count} program stages to standard cancer clinical workflow")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
