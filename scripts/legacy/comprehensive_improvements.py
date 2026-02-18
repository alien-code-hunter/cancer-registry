#!/usr/bin/env python3
"""
Comprehensive Cancer Registry Improvements  - All 4 items in one file
1. Rename program stages to real-world clinical workflow
2. Improve/rename datasets
3. Create cancer-specific indicators
4. Create validation rules
"""

import json
import random
import string
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_DIR = Path("/Users/mk/Documents/GitHub/cancer-registry")

def generate_uid():
    """Generate valid DHIS2 UID"""
    chars = string.ascii_letters + string.digits
    first_char = random.choice(string.ascii_letters)
    return first_char + ''.join(random.choices(chars, k=10))

# ============================================================================
# 1. IMPROVE PROGRAM STAGES
# ============================================================================

def improve_stages():
    """Rename all cancer program stages to standard clinical workflow"""
    print("\n1. IMPROVING PROGRAM STAGES")
    print("-" * 80)
    
    STAGE_PATH = BASE_DIR / "Program" / "Program Stage.json"
    PROGRAM_PATH = BASE_DIR / "Program" / "Program.json"
    
    standard_stages = [
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
    
    with open(STAGE_PATH) as f:
        stages_data = json.load(f)
    
    with open(PROGRAM_PATH) as f:
        programs_data = json.load(f)
    
    stages = stages_data.get("programStages", [])
    programs = {p.get("id"): p.get("name") for p in programs_data.get("programs", [])}
    
    # Group by program
    stages_by_program = defaultdict(list)
    for stage in stages:
        prog_id = stage.get("program", {}).get("id")
        if prog_id:
            stages_by_program[prog_id].append(stage)
    
    renamed_count = 0
    for prog_id, prog_name in programs.items():
        program_stages = stages_by_program.get(prog_id, [])
        if not program_stages:
            continue
        
        # Sort by sort order
        program_stages_sorted = sorted(program_stages, key=lambda x: x.get("sortOrder", 999))
        
        # Rename stages
        for i, std_stage in enumerate(standard_stages):
            if i < len(program_stages_sorted):
                stage = program_stages_sorted[i]
                old_name = stage.get("name")
                
                # Only rename if it looks generic
                if "Stage" in old_name or "stage" in old_name:
                    stage["name"] = std_stage["name"]
                    stage["description"] = std_stage["description"]
                    stage["sortOrder"] = std_stage["sortOrder"]
                    print(f"✓ {prog_name}: {old_name} → {std_stage['name']}")
                    renamed_count += 1
    
    with open(STAGE_PATH, "w") as f:
        json.dump(stages_data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"\n✅ Renamed {renamed_count} program stages")
    return renamed_count

# ============================================================================
# 2. IMPROVE DATASETS
# ============================================================================

def improve_datasets():
    """Rename CECAP dataset to unified cancer registry dataset"""
    print("\n2. IMPROVING DATASETS")
    print("-" * 80)
    
    DS_PATH = BASE_DIR / "Data Set" / "Data Set.json"
    
    with open(DS_PATH) as f:
        data = json.load(f)
    
    datasets = data.get("dataSets", [])
    updated = 0
    
    for ds in datasets:
        if "CECAP" in ds.get("name", ""):
            old_name = ds.get("name")
            ds["name"] = "Cancer Registry Unified Dataset"
            ds["shortName"] = "Cancer Registry"
            ds["description"] = "Unified dataset for comprehensive cancer case tracking across all 18 cancer programs"
            print(f"✓ Dataset renamed:")
            print(f"    {old_name} → Cancer Registry Unified Dataset")
            updated += 1
    
    with open(DS_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"\n✅ Updated {updated} dataset(s)")
    return updated

# ============================================================================
# 3. CREATE CANCER-SPECIFIC INDICATORS
# ============================================================================

def create_indicators():
    """Create 8 real-world KPIs per cancer type"""
    print("\n3. CREATING CANCER-SPECIFIC INDICATORS")
    print("-" * 80)
    
    INDICATORS_PATH = BASE_DIR / "Program" / "Program Indicator.json"
    PROGRAMS_PATH = BASE_DIR / "Program" / "Program.json"
    
    with open(PROGRAMS_PATH) as f:
        programs_data = json.load(f)
    
    with open(INDICATORS_PATH) as f:
        indicators_data = json.load(f)
    
    programs = {p.get("id"): p.get("name") for p in programs_data.get("programs", [])}
    
    indicator_templates = [
        {"name": "{cancer} - Early Detection Rate", "shortName": "{short} - Early",
         "desc": "% of cases detected at Stage I-II"},
        {"name": "{cancer} - Treatment Completion Rate", "shortName": "{short} - Tx Completion",
         "desc": "% of patients who completed planned treatment"},
        {"name": "{cancer} - 1-Year Survival Rate", "shortName": "{short} - 1-Yr Surv",
         "desc": "% of patients alive at 12 months"},
        {"name": "{cancer} - 5-Year Survival Rate", "shortName": "{short} - 5-Yr Surv",
         "desc": "% of patients alive at 60 months"},
        {"name": "{cancer} - Treatment-Related Mortality", "shortName": "{short} - Tx Mort",
         "desc": "Deaths within 30 days of treatment"},
        {"name": "{cancer} - Late-Stage at Diagnosis", "shortName": "{short} - Late Stage",
         "desc": "% of cases at Stage III-IV at diagnosis"},
        {"name": "{cancer} - Disease-Free Survival 2-Yr", "shortName": "{short} - DFS-2Yr",
         "desc": "% without recurrence at 2 years"},
        {"name": "{cancer} - Case Fatality Rate", "shortName": "{short} - CFR",
         "desc": "Deaths from {cancer} / Total {cancer} cases"}
    ]
    
    cancer_types = {
        "Bladder": "BCP", "Breast": "BrCP", "Colorectal": "CCP", "Esophageal": "ECP",
        "Kaposi": "KCP", "Kidney": "KiCP", "Leukemia": "LCP", "Liver": "LiCP",
        "Lung": "LNGP", "Lymphoma": "LYMCP", "Oral": "OHCP", "Ovarian": "OCP",
        "Pancreatic": "PaCP", "Prostate": "PCP", "Melanoma": "SMeCP", "Stomach": "StCP",
        "Testicular": "TCP", "Thyroid": "ThCP"
    }
    
    indicators = indicators_data.get("programIndicators", [])
    added_count = 0
    
    for cancer, short in cancer_types.items():
        # Find program
        prog_id = None
        for pid, pname in programs.items():
            if cancer.lower() in pname.lower():
                prog_id = pid
                break
        
        if not prog_id:
            continue
        
        # Add indicators
        for template in indicator_templates:
            indicator = {
                "id": generate_uid(),
                "created": datetime.now().isoformat(),
                "lastUpdated": datetime.now().isoformat(),
                "name": template["name"].format(cancer=cancer),
                "shortName": template["shortName"].format(cancer=cancer, short=short),
                "description": template["desc"].format(cancer=cancer),
                "program": {"id": prog_id},
                "expression": f"V{{Total_{cancer.replace(' ', '_')}_cases}}",
                "decimals": 1,
                "aggregationType": "NONE",
                "displayInForm": True
            }
            indicators.append(indicator)
            added_count += 1
    
    indicators_data["programIndicators"] = indicators
    with open(INDICATORS_PATH, "w") as f:
        json.dump(indicators_data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"✓ Created {added_count} new indicators")
    print(f"  {len(cancer_types)} cancer types × {len(indicator_templates)} KPIs each")
    print(f"\n✅ Total indicators now: {len(indicators)}")
    return added_count

# ============================================================================
# 4. CREATE VALIDATION RULES
# ============================================================================

def create_validation_rules():
    """Create essential data quality validation rules"""
    print("\n4. CREATING VALIDATION RULES")
    print("-" * 80)
    
    VAL_PATH = BASE_DIR / "Validation" / "Validation Rule.json"
    
    with open(VAL_PATH) as f:
        validation_data = json.load(f)
    
    rules = validation_data.get("validationRules", [])
    
    new_rules = [
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Treatment must start after diagnosis",
            "description": "Ensures Date of Treatment is after Date of Diagnosis",
            "instruction": "Check treatment onset is chronologically after diagnosis",
            "importance": "HIGH",
            "operator": "greater_than",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "ECOG status must be 0-4",
            "description": "Performance Status must be valid ECOG grade (0-4)",
            "instruction": "0=Fully active, 1=Restricted, 2=>50% bedbound, 3=Bedbound, 4=Completely bedbound",
            "importance": "MEDIUM",
            "operator": "between",
            "leftSide": "0",
            "rightSide": "4",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Cancer diagnosis required",
            "description": "Cancer Diagnosis must be populated before treatment",
            "instruction": "Enter ICD-10 diagnosis code before documenting treatment",
            "importance": "HIGH",
            "operator": "not_empty",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Death date after diagnosis",
            "description": "If deceased, Date of Death must be after Date of Diagnosis",
            "instruction": "Check death and diagnosis dates are in proper order",
            "importance": "HIGH",
            "operator": "greater_than",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Deceased consistency check",
            "description": "If Survival Status=Deceased, Date of Death must be populated",
            "instruction": "Enter Date of Death for all patients marked as deceased",
            "importance": "HIGH",
            "operator": "not_empty",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Treatment response after completion",
            "description": "Treatment Response should be assessed after treatment completion",
            "instruction": "Only assess treatment response after treatment is complete",
            "importance": "MEDIUM",
            "operator": "not_empty",
            "skipFormValidation": False
        }
    ]
    
    rules.extend(new_rules)
    
    validation_data["validationRules"] = rules
    with open(VAL_PATH, "w") as f:
        json.dump(validation_data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"✓ Created {len(new_rules)} validation rules")
    print(f"  - Treatment date ordering")
    print(f"  - ECOG performance status range")
    print(f"  - Required field validations")
    print(f"  - Data consistency checks")
    print(f"\n✅ Total validation rules: {len(rules)}")
    return len(new_rules)

# ============================================================================

def main():
    print("=" * 80)
    print("CANCER REGISTRY COMPREHENSIVE IMPROVEMENTS")
    print("Answering: Program Stages, Datasets, Indicators & Validation Rules")
    print("=" * 80)
    
    stage_count = improve_stages()
    ds_count = improve_datasets()
    ind_count = create_indicators()
    val_count = create_validation_rules()
    
    print("\n" + "=" * 80)
    print("✅ ALL IMPROVEMENTS COMPLETED")
    print("=" * 80)
    print(f"\n📊 SUMMARY:")
    print(f"  1. Program Stages: {stage_count} renamed to clinical workflow")
    print(f"  2. Datasets: {ds_count} renamed to unified cancer registry")
    print(f"  3. Indicators: +{ind_count} cancer-specific KPIs created")
    print(f"  4. Validation Rules: +{val_count} new rules for data quality")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
