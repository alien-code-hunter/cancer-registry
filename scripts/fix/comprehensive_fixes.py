# --- Fix 2: IndicatorGroup code uniqueness and UID validity ---
def fix_indicatorgroup_code_and_uid():
    print("\n🔧 Fixing IndicatorGroup code uniqueness and UID validity...")
    ig_path = BASE_DIR / "Indicator" / "indicator group.json"
    if not ig_path.exists():
        print(f"  - IndicatorGroup file not found: {ig_path}")
        return
    with open(ig_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    import random, string
    seen_codes = set()
    for ig in data.get('indicatorGroups', []):
        # Regenerate invalid UID
        uid = ig.get('uid')
        if not uid or len(uid) != 11 or not uid.isalnum():
            ig['uid'] = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
        # Remove or rename duplicate codes
        code = ig.get('code')
        if code in seen_codes:
            ig['code'] = f"{code}_{ig['uid']}"
        seen_codes.add(ig['code'])
    with open(ig_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write('\n')
    print(f"  - Fixed IndicatorGroup codes and UIDs in {ig_path}")
    print("✅ IndicatorGroup code/UID fix complete.")

# --- Fix 3: Dashboard UID regeneration ---
def fix_dashboard_uids():
    print("\n🔧 Regenerating Dashboard UIDs to valid DHIS2 format...")
    dash_dir = BASE_DIR / "Dashboard"
    for file in dash_dir.glob("Dashboard_*.json"):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        changed = False
        for dash in data.get('dashboards', []):
            uid = dash.get('uid')
            if not uid or len(uid) != 11 or not uid.isalnum():
                import random, string
                dash['uid'] = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
                changed = True
        if changed:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Fixed Dashboard UIDs in {file}")
    print("✅ Dashboard UID regeneration complete.")

# --- Fix 4: Remove avatar property from all Users ---
def remove_user_avatars():
    print("\n🔧 Removing avatar property from all Users...")
    user_path = BASE_DIR / "Users" / "User.json"
    if not user_path.exists():
        print(f"  - User file not found: {user_path}")
        return
    with open(user_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    changed = False
    for user in data.get('users', []):
        if 'avatar' in user:
            user.pop('avatar')
            changed = True
    if changed:
        with open(user_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Removed avatar property in {user_path}")
    print("✅ User avatar removal complete.")

# --- Fix 5: ValidationRule leftSide/rightSide deserialization errors ---
def fix_validationrule_sides():
    print("\n🔧 Fixing ValidationRule leftSide/rightSide deserialization errors...")
    vr_path = BASE_DIR / "Validation" / "Validation Rule.json"
    if not vr_path.exists():
        print(f"  - ValidationRule file not found: {vr_path}")
        return
    with open(vr_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    changed = False
    for vr in data.get('validationRules', []):
        # Fix leftSide/rightSide
        for side in ['leftSide', 'rightSide']:
            if side in vr and isinstance(vr[side], str):
                vr[side] = {'expression': vr[side]}
                changed = True
            elif side not in vr:
                vr[side] = {'expression': ''}
                changed = True
        # Replace invalid operator values
        if vr.get('operator') == 'not_empty':
            vr['operator'] = 'compulsory_pair'
            changed = True
        # Add missing periodType
        if 'periodType' not in vr:
            vr['periodType'] = 'Monthly'
            changed = True
    if changed:
        with open(vr_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Fixed ValidationRule sides, operator, and periodType in {vr_path}")
    print("✅ ValidationRule leftSide/rightSide, operator, and periodType fix complete.")
# --- Fix 1: Truncate DataElement shortName ---
def truncate_dataelement_shortnames():
    print("\n🔧 Truncating DataElement shortName to 50 chars for all cancer-type files...")
    data_element_dir = BASE_DIR / "Data Element"
    for file in data_element_dir.glob("Data_Element_*.json"):
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        changed = False
        for de in data.get('dataElements', []):
            if 'shortName' in de and len(de['shortName']) > 50:
                de['shortName'] = de['shortName'][:50]
                changed = True
        if changed:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Fixed shortName in {file}")
    print("✅ DataElement shortName truncation complete.")
import json
from pathlib import Path
from collections import defaultdict
import tempfile
import shutil
try:
    import ijson
except ImportError:
    ijson = None

BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
                          'Kaposi', 'Melanoma', 'Cervical']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break
            if not cancer_type:
                cancer_type = 'Generic'
            items = dashboard.get('dashboardItems', [])
            for item in items:
                if 'type' not in item or not item.get('type'):
                    if item.get('visualization'):
                        item['type'] = 'VISUALIZATION'
                    elif item.get('eventChart'):
                        item['type'] = 'EVENT_CHART'
                    elif item.get('map'):
                        item['type'] = 'MAP'
                    elif item.get('appKey'):
                        item['type'] = 'APP'
                    else:
                        item['type'] = 'VISUALIZATION'
                    items_fixed += 1
            dashboards_by_cancer[cancer_type].append(dashboard)
    for cancer, dashboards in dashboards_by_cancer.items():
        out_path = BASE_DIR / "Dashboard" / f"Dashboard_{cancer}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'dashboards': dashboards}, f, indent=2, ensure_ascii=True)
            f.write('\n')
        print(f"  - Created {out_path} with {len(dashboards)} dashboards")
    print(f"✅ Fixed {items_fixed} dashboard items and split dashboards by cancer type.")
    return items_fixed
# Add missing function to split program stages by cancer type
def assign_data_elements_to_stages_split(stages, cancer_de_map, cancer_stages):
    print("\n2️⃣ SPLITTING PROGRAM STAGES AND DATA ELEMENTS BY CANCER TYPE")
    print("-" * 80)
    # Process and write each cancer's program stages one at a time
    cancer_types = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
        'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
        'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
        'Kaposi', 'Melanoma', 'Cervical', 'Generic']
    total_written = 0
    for cancer in cancer_types:
        cancer_stages_list = []
        for idx, stage in enumerate(stages, 1):
            # Determine if this stage belongs to the current cancer type
            stage_cancer_type = None
            name = stage.get('name', '')
            prog_id = stage.get('program', {}).get('id', '')
            for c in cancer_stages:
                if any(s['id'] == stage.get('id') for s in cancer_stages[c]):
                    stage_cancer_type = c
                    break
            if not stage_cancer_type:
                for c in cancer_types:
                    if c.lower() in name.lower() or c.lower() in prog_id.lower():
                        stage_cancer_type = c
                        break
            if not stage_cancer_type:
                stage_cancer_type = 'Generic'
            if stage_cancer_type != cancer:
                continue
            # Assign data elements
            elements_to_add = cancer_de_map.get(cancer, []) + cancer_de_map.get('Generic', [])
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
            cancer_stages_list.append(stage)
            if len(cancer_stages_list) % 10 == 0:
                print(f"  [{cancer}] Processed {len(cancer_stages_list)} stages...")
        if cancer_stages_list:
            out_path = BASE_DIR / "Program" / f"Program_Stage_{cancer}.json"
            if out_path.exists():
                print(f"  - Skipping {out_path} (already exists)")
                continue
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump({'programStages': cancer_stages_list}, f, indent=2, ensure_ascii=True)
                f.write('\n')
            print(f"  - Created {out_path} with {len(cancer_stages_list)} stages")
            total_written += len(cancer_stages_list)
    print(f"✅ Split program stages and assigned data elements by cancer type.")
    return total_written
#!/usr/bin/env python3
"""
Comprehensive Fix Script for Cancer Registry Issues:
1. Fix dashboards - add missing item type
2. Assign data elements to program stages
3. Rename CECAP to Cervical Cancer
4. Fix event visualizer conflicts
5. Group data elements by cancer type
"""


BASE_DIR = Path(__file__).resolve().parents[2]

def issue_1_split_dashboards_by_cancer():
    print("\n1️⃣ SPLITTING DASHBOARDS BY CANCER TYPE")
    print("-" * 80)
    db_path = BASE_DIR / "Dashboard" / "Dashboard.json"
    if ijson is None:
        print("❌ ijson is not installed. Please install it with 'pip install ijson'.")
        return 0
    dashboards_by_cancer = defaultdict(list)
    items_fixed = 0
    with open(db_path, 'r', encoding='utf-8') as infile:
        for dashboard in ijson.items(infile, 'dashboards.item'):
            cancer_type = None
            dash_name = dashboard.get('name', '')
            for cancer in ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
                          'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
                          'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal']:
                if cancer.lower() in dash_name.lower():
                    cancer_type = cancer
                    break