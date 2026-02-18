#!/usr/bin/env python3
"""
Fix Program Stages - Version 3
Properly handles stages stored in Program Stage.json with program references
"""

import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/mk/Documents/GitHub/cancer-registry")

# Standard clinical workflow stages
STANDARD_STAGES = [
    {"name": "1. Initial Assessment & Diagnostics",
     "desc": "Patient presentation - chief complaint, risk factors, symptoms, ECOG status",
     "sortOrder": 1},
    {"name": "2. Staging & Treatment Planning",
     "desc": "TNM staging, risk assessment, multidisciplinary treatment plan",
     "sortOrder": 2},
    {"name": "3. Active Treatment",
     "desc": "Treatment execution - compliance, toxicity monitoring, adjustments",
     "sortOrder": 3},
    {"name": "4. Follow-up & Outcomes",
     "desc": "Long-term monitoring - surveillance, recurrence, survival outcomes",
     "sortOrder": 4}
]

def get_program_mapping():
    """Build mapping of program IDs to cancer names"""
    prog_map = {}
    
    # Get CECAP from Program.json
    with open(BASE_DIR / "Program" / "Program.json") as f:
        prog_data = json.load(f)
        for prog in prog_data.get("programs", []):
            prog_map[prog.get("id")] = prog.get("name")
    
    # Get other cancers from individual files
    cancer_files = list((BASE_DIR / "Program").glob("*Cancer Program.json"))
    for cf in sorted(cancer_files):
        with open(cf) as f:
            pdata = json.load(f)
            for prog in pdata.get("programs", []):
                prog_map[prog.get("id")] = prog.get("name")
    
    return prog_map

def main():
    print("\n" + "="*80)
    print("FIXING PROGRAM STAGES - CONSOLIDATED APPROACH")
    print("="*80 + "\n")
    
    # Get program mapping
    prog_map = get_program_mapping()
    print(f"Found {len(prog_map)} programs:")
    for pid, pname in sorted(prog_map.items()):
        print(f"  - {pname} ({pid})")
    
    # Load stages
    stage_path = BASE_DIR / "Program" / "Program Stage.json"
    with open(stage_path) as f:
        stage_data = json.load(f)
    
    stages = stage_data.get("programStages", [])
    
    # Group stages by program
    stages_by_prog = defaultdict(list)
    for stage in stages:
        prog_id = stage.get("program", {}).get("id")
        if prog_id:
            stages_by_prog[prog_id].append(stage)
    
    print(f"\nGrouped {len(stages)} stages by program:")
    for pid in sorted(stages_by_prog.keys()):
        pname = prog_map.get(pid, "Unknown")
        stage_count = len(stages_by_prog[pid])
        print(f"  - {pname}: {stage_count} stages")
    
    # Rename stages per program
    total_renamed = 0
    
    for prog_id, prog_stages in stages_by_prog.items():
        prog_name = prog_map.get(prog_id, "Unknown")
        
        # Sort stages by current sort order
        prog_stages_sorted = sorted(prog_stages, key=lambda x: x.get("sortOrder", 999))
        
        print(f"\n{prog_name}:")
        
        # Update each stage with standard names
        for i, stage in enumerate(prog_stages_sorted):
            if i < len(STANDARD_STAGES):
                old_name = stage.get("name")
                new_name = STANDARD_STAGES[i]["name"]
                stage["name"] = new_name
                stage["description"] = STANDARD_STAGES[i]["desc"]
                stage["sortOrder"] = STANDARD_STAGES[i]["sortOrder"]
                
                print(f"  ✓ {old_name} → {new_name}")
                total_renamed += 1
    
    # Save updated stages
    stage_data["programStages"] = stages
    with open(stage_path, "w") as f:
        json.dump(stage_data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"\n{'='*80}")
    print(f"✅ Successfully renamed {total_renamed} program stages")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
