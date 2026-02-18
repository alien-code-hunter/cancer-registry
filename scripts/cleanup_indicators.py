#!/usr/bin/env python3
"""
Clean up indicators - remove those without program references
"""

import json
from pathlib import Path

BASE_DIR = Path("/Users/mk/Documents/GitHub/cancer-registry")

def main():
    print("\n" + "="*80)
    print("CLEANING UP INDICATORS - REMOVE THOSE WITHOUT PROGRAM REFERENCES")
    print("="*80 + "\n")
    
    # Load indicators
    ind_path = BASE_DIR / "Program" / "Program Indicator.json"
    with open(ind_path) as f:
        ind_data = json.load(f)
    
    indicators = ind_data.get("programIndicators", [])
    print(f"Starting with {len(indicators)} indicators\n")
    
    # Filter out indicators without program
    valid_indicators = [ind for ind in indicators if ind.get("program")]
    removed_count = len(indicators) - len(valid_indicators)
    
    print(f"Indicators with program reference: {len(valid_indicators)}")
    print(f"Indicators without program reference (removed): {removed_count}")
    
    # Show examples of what we're removing
    if removed_count > 0:
        print("\nExamples of removed indicators:")
        removed = [ind for ind in indicators if not ind.get("program")][:5]
        for ind in removed:
            print(f"  - {ind.get('name', 'Unknown')}")
    
    # Save cleaned indicators
    ind_data["programIndicators"] = valid_indicators
    with open(ind_path, "w") as f:
        json.dump(ind_data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"\n✅ Cleaned up indicators: {removed_count} removed")
    print(f"✅ Final indicator count: {len(valid_indicators)}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
