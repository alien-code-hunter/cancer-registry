#!/usr/bin/env python3
"""
Comprehensive project audit - identify all issues
"""
import json
import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parents[2]

def validate_json_files():
    """Check all JSON files for validity"""
    print("=" * 80)
    print("1. JSON SYNTAX VALIDATION")
    print("=" * 80)
    
    valid_files = 0
    invalid_files = 0
    errors = []
    
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip hidden directories and node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, BASE_DIR)
                
                try:
                    with open(filepath, 'r') as f:
                        json.load(f)
                    valid_files += 1
                except json.JSONDecodeError as e:
                    invalid_files += 1
                    errors.append((rel_path, str(e)))
                except Exception as e:
                    invalid_files += 1
                    errors.append((rel_path, str(e)))
    
    print(f"\n✅ Valid JSON files: {valid_files}")
    if invalid_files > 0:
        print(f"❌ Invalid JSON files: {invalid_files}")
        for filepath, error in errors:
            print(f"   - {filepath}: {error[:100]}")
    else:
        print(f"✅ No JSON syntax errors found")
    
    return invalid_files == 0

def validate_data_consistency():
    """Check for data consistency issues"""
    print("\n" + "=" * 80)
    print("2. DATA CONSISTENCY CHECKS")
    print("=" * 80)
    
    issues = []
    
    # Load all data
    with open(f"{BASE_DIR}/Program/Program.json") as f:
        programs = json.load(f).get('programs', [])
    program_ids = {p.get('id') for p in programs}
    
    with open(f"{BASE_DIR}/Program/Program Stage.json") as f:
        stages = json.load(f).get('programStages', [])
    stage_ids = {s.get('id') for s in stages}
    stage_program_refs = defaultdict(list)
    
    for stage in stages:
        prog_ref = stage.get('program', {})
        prog_id = prog_ref.get('id') if isinstance(prog_ref, dict) else prog_ref
        if prog_id:
            stage_program_refs[prog_id].append(stage.get('id'))
    
    with open(f"{BASE_DIR}/Program/Program Indicator.json") as f:
        indicators = json.load(f).get('programIndicators', [])
    
    with open(f"{BASE_DIR}/Data Element/Data Element.json") as f:
        data_elements = json.load(f).get('dataElements', [])
    de_ids = {de.get('id') for de in data_elements}
    
    with open(f"{BASE_DIR}/Dashboard/Dashboard.json") as f:
        dashboards = json.load(f).get('dashboards', [])
    
    # Check program references
    print("\n✓ Checking Program References...")
    orphaned_stages = 0
    for prog_id in stage_program_refs.keys():
        if prog_id not in program_ids:
            orphaned_stages += stage_program_refs[prog_id].__len__()
            issues.append(f"Stages reference non-existent program {prog_id}")
    
    if orphaned_stages == 0:
        print(f"  ✅ All {len(stages)} stages reference valid programs")
    else:
        print(f"  ❌ {orphaned_stages} stages have orphaned program references")
    
    # Check program stage data element references
    print("\n✓ Checking Program Stage Data Element References...")
    invalid_de_refs = 0
    for stage in stages:
        for item in stage.get('programStageDataElements', []):
            de_id = item.get('dataElement', {}).get('id')
            if de_id and de_id not in de_ids:
                invalid_de_refs += 1
                issues.append(f"Stage {stage.get('id')} references non-existent data element {de_id}")
    
    if invalid_de_refs == 0:
        print(f"  ✅ All program stage data element references valid")
    else:
        print(f"  ❌ {invalid_de_refs} invalid data element references")
    
    # Check indicator program references
    print("\n✓ Checking Program Indicator Program References...")
    invalid_ind_refs = 0
    for ind in indicators:
        prog_ref = ind.get('program', {})
        prog_id = prog_ref.get('id') if isinstance(prog_ref, dict) else prog_ref
        if prog_id and prog_id not in program_ids:
            invalid_ind_refs += 1
    
    if invalid_ind_refs == 0:
        print(f"  ✅ All {len(indicators)} indicators reference valid programs")
    else:
        print(f"  ❌ {invalid_ind_refs} indicators have invalid program references")
    
    # Check dashboard items
    print("\n✓ Checking Dashboard Items...")
    items_without_type = 0
    for dashboard in dashboards:
        for item in dashboard.get('dashboardItems', []):
            if 'type' not in item:
                items_without_type += 1
    
    if items_without_type == 0:
        print(f"  ✅ All dashboard items have type field")
    else:
        print(f"  ❌ {items_without_type} dashboard items missing type field")
    
    return len(issues) == 0

def check_file_coverage():
    """Check which files are in the project"""
    print("\n" + "=" * 80)
    print("3. PROJECT FILE COVERAGE")
    print("=" * 80)

    metadata_folders = [
        "Attribute",
        "Category",
        "Dashboard",
        "Data Element",
        "Data Set",
        "Event Visualisation",
        "Options",
        "Organisation Unit",
        "Program",
        "Program Rule",
        "Tracked Entity",
        "Users",
        "Validation",
        "Visualisation",
    ]

    folders = {}
    for folder in metadata_folders:
        path = BASE_DIR / folder
        if path.is_dir():
            json_count = len([f for f in os.listdir(path) if f.endswith('.json')])
            folders[folder] = json_count

    nested_folders = ["artifacts", "docs"]
    for folder in nested_folders:
        path = BASE_DIR / folder
        if not path.is_dir():
            continue
        json_count = 0
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            json_count += sum(1 for f in files if f.endswith('.json'))
        folders[folder] = json_count

    print("\nFolders with JSON files:")
    for folder in sorted(folders.keys()):
        count = folders[folder]
        status = "✅" if count > 0 else "⚠️"
        print(f"  {status} {folder}: {count} files")

def main():
    print("\n")
    print("█" * 80)
    print("COMPREHENSIVE PROJECT AUDIT - CANCER REGISTRY")
    print("█" * 80)
    
    json_ok = validate_json_files()
    consistency_ok = validate_data_consistency()
    check_file_coverage()
    
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"JSON Syntax: {'✅ OK' if json_ok else '❌ ISSUES'}")
    print(f"Data Consistency: {'✅ OK' if consistency_ok else '❌ ISSUES'}")
    print("=" * 80)

if __name__ == "__main__":
    main()
