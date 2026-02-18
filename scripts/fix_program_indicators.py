#!/usr/bin/env python3
"""
Fix Program Indicators - Add proper program references
"""

import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/mk/Documents/GitHub/cancer-registry")

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
    print("FIXING PROGRAM INDICATORS - ADD PROPER PROGRAM REFERENCES")
    print("="*80 + "\n")
    
    # Get program mapping
    prog_map = get_program_mapping()
    print(f"Found {len(prog_map)} programs\n")
    
    # Load indicators
    ind_path = BASE_DIR / "Program" / "Program Indicator.json"
    with open(ind_path) as f:
        ind_data = json.load(f)
    
    indicators = ind_data.get("programIndicators", [])
    print(f"Processing {len(indicators)} indicators...\n")
    
    # Track which indicators are missing program refs
    missing_prog = []
    with_prog = []
    fixed = []
    
    for indicator in indicators:
        ind_name = indicator.get("name", "Unknown")
        
        # Check if has program
        if not indicator.get("program"):
            missing_prog.append(indicator)
            
            # Try to match to a program by name
            for prog_id, prog_name in prog_map.items():
                cancer_name = prog_name.replace(" Program", "").replace("Cancer ", "").strip()
                
                # Check if cancer name is in indicator name
                if cancer_name.lower() in ind_name.lower():
                    indicator["program"] = {"id": prog_id}
                    fixed.append((ind_name, prog_name))
                    break
        else:
            with_prog.append(indicator)
    
    print(f"✓ Indicators with program reference: {len(with_prog)}")
    print(f"✓ Indicators without program reference: {len(missing_prog)}")
    print(f"✓ Fixed through name matching: {len(fixed)}\n")
    
    if fixed:
        print("Fixed indicators (examples):")
        for ind_name, prog_name in fixed[:10]:
            print(f"  - {ind_name[:50]}...")
            print(f"    → {prog_name}")
    
    # Count by cancer type
    print(f"\nIndicators by program:")
    prog_counts = defaultdict(int)
    for indicator in indicators:
        prog_id = indicator.get("program", {}).get("id") if indicator.get("program") else None
        if prog_id:
            prog_name = prog_map.get(prog_id, "Unknown")
            prog_counts[prog_name] += 1
    
    for prog_name in sorted(prog_counts.keys()):
        print(f"  - {prog_name}: {prog_counts[prog_name]} indicators")
    
    # Save updated indicators
    ind_data["programIndicators"] = indicators
    with open(ind_path, "w") as f:
        json.dump(ind_data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"\n{'='*80}")
    print(f"✅ Successfully processed {len(indicators)} indicators")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
