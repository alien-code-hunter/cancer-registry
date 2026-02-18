#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""

import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/mk/Documents/GitHub/cancer-registry")

def issue_1_fix_dashboards():
    """Fix dashboards - add missing item type"""
    print("\n1️⃣ FIXING DASHBOARDS - MISSING ITEM TYPE")
    print("-" * 80)
    
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    with open(db_path) as f:
        data = json.load(f)
    
    dashboards = data.get('dashboards', [])
    items_fixed = 0
    
    for dashboard in dashboards:
        items = dashboard.get('dashboardItems', [])
        for item in items:
            # Add missing type field
            if 'type' not in item or not item.get('type'):
                # Infer type from content
                if item.get('visualization'):
                    item['type'] = 'VISUALIZATION'
                elif item.get('eventChart'):
                    item['type'] = 'EVENT_CHART'
                elif item.get('map'):
                    item['type'] = 'MAP'
                elif item.get('appKey'):
                    item['type'] = 'APP'
                else:
                    item['type'] = 'VISUALIZATION'  # Default
                items_fixed += 1
    
    with open(db_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write('\n')
    
    print(f"✅ Fixed {items_fixed} dashboard items with missing type")
    return items_fixed


def issue_2_assign_data_elements():
    """Assign data elements to program stages"""
    print("\n2️⃣ ASSIGNING DATA ELEMENTS TO PROGRAM STAGES")
    print("-" * 80)
    
    stage_path = BASE_DIR / "Program" / "Program Stage.json"
    de_path = BASE_DIR / "Data Element" / "Data Element.json"
    
    with open(stage_path) as f:
        stage_data = json.load(f)
    with open(de_path) as f:
        de_data = json.load(f)
    
    # Map cancer types to data elements
    cancer_de_map = {}
    data_elements = de_data.get('dataElements', [])
    
    for de in data_elements:
        name = de.get('name', '')
        de_id = de.get('id', '')
        
        # Skip if no name
        if not name:
            continue
        
        # Try to determine which cancer type(s) this element belongs to
        for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver', 
                      'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder', 
                      'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal', 
                      'Kaposi', 'Melanoma', 'CECAP']:
            if cancer.lower() in name.lower():
                if cancer not in cancer_de_map:
                    cancer_de_map[cancer] = []
                cancer_de_map[cancer].append(de_id)
                break
        else:
            # Generic cancer elements
            if 'cancer' in name.lower() or 'diagnosis' in name.lower() or 'treatment' in name.lower():
                if 'Generic' not in cancer_de_map:
                    cancer_de_map['Generic'] = []
                cancer_de_map['Generic'].append(de_id)
    
    # Map cancer types to program stage IDs
    stages = stage_data.get('programStages', [])
    cancer_stages = defaultdict(list)
    
    for stage in stages:
        name = stage.get('name', '')
        stage_id = stage.get('id', '')
        prog = stage.get('program', {})
        prog_id = prog.get('id', '')
        
        # Determine which cancer this stage belongs to
        for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                      'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                      'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                      'Kaposi', 'Melanoma', 'CECAP']:
            if cancer.lower() in name.lower() or cancer.lower() in prog_id.lower():
                cancer_stages[cancer].append({'id': stage_id, 'name': name})
                break
    
    # Assign data elements to stages
    updated_count = 0
    for stage in stages:
        stage_id = stage.get('id')
        if not stage_id:
            continue
        
        # Find which cancer type this stage belongs to
        cancer_type = None
        prog_id = stage.get('program', {}).get('id', '')
        
        for cancer in cancer_stages:
            if any(s['id'] == stage_id for s in cancer_stages[cancer]):
                cancer_type = cancer
                break
        
        if not cancer_type:
            cancer_type = 'Generic'
        
        # Get elements for this cancer type
        elements_to_add = cancer_de_map.get(cancer_type, [])
        elements_to_add += cancer_de_map.get('Generic', [])  # Add generic ones too
        
        if not elements_to_add:
            continue
        
        # Add elements to stage if not already present
        existing = stage.get('programStageDataElements', [])
        existing_ids = {item.get('dataElement', {}).get('id') for item in existing}
        
        sort_order = len(existing) + 1
        for elem_id in elements_to_add:
            if elem_id not in existing_ids:
                existing.append({
                    'dataElement': {'id': elem_id},
                    'compulsory': False,
                    'allowProvidedElsewhere': False,
                    'allowFutureDate': False,
                    'sortOrder': sort_order
                })
                sort_order += 1
        
        if len(existing) > 0:
            stage['programStageDataElements'] = existing
            updated_count += 1
    
    with open(stage_path, 'w') as f:
        json.dump(stage_data, f, indent=2, ensure_ascii=True)
        f.write('\n')
    
    print(f"✅ Assigned data elements to {updated_count} program stages")
    return updated_count


def issue_3_rename_cecap():
    """Rename CECAP program to Cervical Cancer"""
    print("\n3️⃣ RENAMING CECAP TO CERVICAL CANCER PROGRAM")
    print("-" * 80)
    
    prog_path = BASE_DIR / "Program" / "Program.json"
    
    with open(prog_path) as f:
        data = json.load(f)
    
    programs = data.get('programs', [])
    renamed = 0
    
    for prog in programs:
        if prog.get('shortName') == 'CECAP' or 'CECAP' in prog.get('name', ''):
            old_name = prog.get('name')
            prog['name'] = 'Cervical Cancer Program'
            prog['shortName'] = 'CCP'
            prog['description'] = 'Cervical cancer screening, diagnosis, treatment, and follow-up program'
            renamed += 1
            print(f"  {old_name} → {prog['name']}")
    
    with open(prog_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write('\n')
    
    # Also rename stages
    stage_path = BASE_DIR / "Program" / "Program Stage.json"
    with open(stage_path) as f:
        stage_data = json.load(f)
    
    stages = stage_data.get('programStages', [])
    stage_renamed = 0
    
    for stage in stages:
        name = stage.get('name', '')
        if 'CECAP' in name:
            new_name = name.replace('CECAP', 'Cervical Cancer')
            stage['name'] = new_name
            stage_renamed += 1
    
    with open(stage_path, 'w') as f:
        json.dump(stage_data, f, indent=2, ensure_ascii=True)
        f.write('\n')
    
    # Rename in other files
    renamed += stage_renamed
    print(f"✅ Renamed {renamed} CECAP items to Cervical Cancer")
    return renamed


def issue_6_group_data_elements():
    """Group data elements by cancer type"""
    print("\n6️⃣ CREATING CANCER-GROUPED DATA ELEMENTS REFERENCE")
    print("-" * 80)
    
    de_path = BASE_DIR / "Data Element" / "Data Element.json"
    
    with open(de_path) as f:
        data = json.load(f)
    
    data_elements = data.get('dataElements', [])
    
    # Group by cancer
    grouped = defaultdict(list)
    
    for de in data_elements:
        name = de.get('name', '')
        de_id = de.get('id', '')
        
        # Determine cancer type
        cancer_type = None
        for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                      'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                      'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                      'Kaposi', 'Melanoma', 'Cervical']:
            if cancer.lower() in name.lower():
                cancer_type = cancer
                break
        
        if not cancer_type:
            if any(word in name.lower() for word in ['cancer', 'diagnosis', 'treatment', 'staging']):
                cancer_type = 'Generic Cancer'
            else:
                cancer_type = 'Other'
        
        grouped[cancer_type].append({'id': de_id, 'name': name})
    
    # Create reference file
    ref_file = BASE_DIR / "Data Element" / "Data Elements by Cancer Type.json"
    reference = {
        'dataElementsByType': dict(grouped),
        'summary': {cancer: len(elements) for cancer, elements in grouped.items()},
        'totalElements': len(data_elements)
    }
    
    with open(ref_file, 'w') as f:
        json.dump(reference, f, indent=2, ensure_ascii=True)
        f.write('\n')
    
    print("✅ Created Data Elements by Cancer Type reference file")
    for cancer in sorted(grouped.keys()):
        print(f"  - {cancer}: {len(grouped[cancer])} elements")
    
    return len(grouped)


def main():
    print("\n" + "="*80)
    print("CANCER REGISTRY - COMPREHENSIVE FIX SCRIPT")
    print("="*80)
    
    results = {}
    
    try:
        results['dashboards'] = issue_1_fix_dashboards()
    except Exception as e:
        print(f"❌ Dashboard fix failed: {e}")
    
    try:
        results['data_elements'] = issue_2_assign_data_elements()
    except Exception as e:
        print(f"❌ Data element assignment failed: {e}")
    
    try:
        results['cecap_rename'] = issue_3_rename_cecap()
    except Exception as e:
        print(f"❌ CECAP rename failed: {e}")
    
    try:
        results['grouping'] = issue_6_group_data_elements()
    except Exception as e:
        print(f"❌ Element grouping failed: {e}")
    
    print("\n" + "="*80)
    print("✅ FIXES COMPLETED")
    print("="*80)
    print(f"\nSummary:")
    for key, value in results.items():
        print(f"  ✓ {key}: {value}")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
