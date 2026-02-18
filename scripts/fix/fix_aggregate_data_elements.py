#!/usr/bin/env python3
"""
Fix Program Stages - Remove AGGREGATE data elements, keep only TRACKER
"""
import json

# Load data elements and identify TRACKER vs AGGREGATE
with open('Data Element/Data Element.json') as f:
    de_data = json.load(f)

tracker_elements = set()
aggregate_elements = set()

for de in de_data.get('dataElements', []):
    de_id = de.get('id')
    domain = de.get('domainType', 'UNKNOWN')
    
    if domain == 'TRACKER':
        tracker_elements.add(de_id)
    elif domain == 'AGGREGATE':
        aggregate_elements.add(de_id)

print(f"Data Elements Analysis:")
print(f"  ✅ TRACKER: {len(tracker_elements)} (OK for program stages)")
print(f"  ❌ AGGREGATE: {len(aggregate_elements)} (must be removed)")

# Load and fix program stages
with open('Program/Program Stage.json') as f:
    stage_data = json.load(f)

fixed_count = 0
removed_count = 0

for stage in stage_data.get('programStages', []):
    current_elements = stage.get('programStageDataElements', []) or []
    
    # Filter to keep only TRACKER type data elements
    tracker_only = []
    for item in current_elements:
        de_id = item.get('dataElement', {}).get('id')
        if de_id in tracker_elements:
            tracker_only.append(item)
        elif de_id in aggregate_elements:
            removed_count += 1
    
    if len(tracker_only) < len(current_elements):
        stage['programStageDataElements'] = tracker_only
        fixed_count += 1

# Save corrected version
with open('Program/Program Stage.json', 'w') as f:
    json.dump(stage_data, f, indent=2, ensure_ascii=True)
    f.write('\n')

print(f"\nProgram Stages Fixed:")
print(f"  ✅ Fixed {fixed_count} stages by removing AGGREGATE elements")
print(f"  ✅ Removed {removed_count} AGGREGATE data element references")
print(f"  ✅ Kept {len(tracker_elements)} TRACKER data elements")
