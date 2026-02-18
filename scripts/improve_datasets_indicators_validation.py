#!/usr/bin/env python3
"""
2-4. Improve datasets, create cancer-specific indicators, and validation rules.
"""

import json
import uuid
import random
import string
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]

def generate_uid():
    """Generate a valid DHIS2 UID (11 chars, starts with letter)"""
    chars = string.ascii_letters + string.digits
    first_char = random.choice(string.ascii_letters)
    remaining = ''.join(random.choices(chars, k=10))
    return first_char + remaining

# ============================================================================
# 2. DATASET IMPROVEMENTS
# ============================================================================

def improve_datasets():
    """Rename CECAP dataset to Cancer Registry Dataset to cover all cancers"""
    ds_path = BASE_DIR / "Data Set" / "Data Set.json"
    
    with open(ds_path) as f:
        data = json.load(f)
    
    datasets = data.get("dataSets", [])
    updated = 0
    
    for ds in datasets:
        if "CECAP" in ds.get("name", ""):
            old_name = ds.get("name")
            ds["name"] = "Cancer Registry Unified Dataset"
            ds["shortName"] = "Cancer Registry Data"
            ds["description"] = "Unified dataset for comprehensive cancer case tracking across all cancer types"
            print(f"✓ Dataset renamed:")
            print(f"    OLD: {old_name}")
            print(f"    NEW: Cancer Registry Unified Dataset")
            updated += 1
    
    with open(ds_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    return updated

# ============================================================================
# 3. CANCER-SPECIFIC INDICATORS
# ============================================================================

def create_cancer_indicators():
    """Create 8 real-world cancer-specific indicators per cancer type"""
    indicators_path = BASE_DIR / "Program" / "Program Indicator.json"
    programs_path = BASE_DIR / "Program" / "Program.json"
    
    with open(programs_path) as f:
        programs_data = json.load(f)
    
    with open(indicators_path) as f:
        indicators_data = json.load(f)
    
    programs = {p.get("id"): p.get("name") for p in programs_data.get("programs", [])}
    
    # Template indicators
    indicator_templates = [
        {
            "name": "{cancer} - Early Detection Rate",
            "shortName": "{short} - Early Detection",
            "description": "Percentage of {cancer} cases detected at Stage I-II",
            "expression": "V{{Stage_I_II_{Cancer}}} / V{{Total_{Cancer}}} * 100"
        },
        {
            "name": "{cancer} - Treatment Completion Rate",
            "shortName": "{short} - Treatment Completion",
            "description": "Percentage of {cancer} patients who completed their planned treatment",
            "expression": "V{{Completed_{Cancer}}} / V{{Treatment_Plan_{Cancer}}} * 100"
        },
        {
            "name": "{cancer} - 1-Year Survival Rate",
            "shortName": "{short} - 1-Yr Survival",
            "description": "Percentage of {cancer} patients surviving at 12 months",
            "expression": "V{{Alive_12m_{Cancer}}} / V{{Total_{Cancer}}} * 100"
        },
        {
            "name": "{cancer} - 5-Year Survival Rate",
            "shortName": "{short} - 5-Yr Survival",
            "description": "Percentage of {cancer} patients surviving at 60 months",
            "expression": "V{{Alive_60m_{Cancer}}} / V{{Total_{Cancer}}} * 100"
        },
        {
            "name": "{cancer} - Treatment-Related Mortality",
            "shortName": "{short} - Tx Mortality",
            "description": "Deaths within 30 days of treatment initiation in {cancer} patients",
            "expression": "V{{Death_30d_{Cancer}}} / V{{Treated_{Cancer}}} * 100"
        },
        {
            "name": "{cancer} - Late-Stage Diagnosis Rate",
            "shortName": "{short} - Late Stage",
            "description": "Percentage of {cancer} cases at Stage III-IV at diagnosis",
            "expression": "V{{Stage_III_IV_{Cancer}}} / V{{Total_{Cancer}}} * 100"
        },
        {
            "name": "{cancer} - Disease-Free Survival 2-Year",
            "shortName": "{short} - DFS 2-Yr",
            "description": "Percentage of {cancer} patients without recurrence at 2 years",
            "expression": "V{{NoRecurrence_24m_{Cancer}}} / V{{Total_{Cancer}}} * 100"
        },
        {
            "name": "{cancer} - Median Overall Survival (months)",
            "shortName": "{short} - Median OS",
            "description": "Median overall survival in months for {cancer} patients",
            "expression": "Median(Survival_months_{Cancer})"
        }
    ]
    
    indicators = indicators_data.get("programIndicators", [])
    
    # Cancer type mapping
    cancer_types = {
        "Bladder": "BCP",
        "Breast": "BrCP",
        "Colorectal": "CCP",
        "Esophageal": "ECP",
        "Kaposi": "KCP",
        "Kidney": "KiCP",
        "Leukemia": "LCP",
        "Liver": "LiCP",
        "Lung": "LNGP",
        "Lymphoma": "LYMCP",
        "Oral": "OHCP",
        "Ovarian": "OCP",
        "Pancreatic": "PaCP",
        "Prostate": "PCP",
        "Melanoma": "SMeCP",
        "Stomach": "StCP",
        "Testicular": "TCP",
        "Thyroid": "ThCP"
    }
    
    adding_count = 0
    for cancer_name, cancer_short in cancer_types.items():
        # Find program
        prog_id = None
        for pid, pname in programs.items():
            if cancer_name.lower() in pname.lower():
                prog_id = pid
                break
        
        if not prog_id:
            print(f"⚠️  Could not find program for {cancer_name}")
            continue
        
        # Create indicators for this cancer
        for template in indicator_templates:
            indicator = {
                "id": generate_uid(),
                "created": datetime.now().isoformat(),
                "lastUpdated": datetime.now().isoformat(),
                "name": template["name"].format(cancer=cancer_name),
                "shortName": template["shortName"].format(cancer=cancer_name, short=cancer_short),
                "description": template["description"].format(cancer=cancer_name),
                "program": {"id": prog_id},
                "expression": template["expression"].format(Cancer=cancer_name.replace(" ", "_")),
                "decimals": 2,
                "indicatorType": {"id": "bWuNrMKHEoZ"},  # Standard type
                "aggregationType": "NONE",
                "displayInForm": True,
                "sharing": {
                    "owner": "M5zQapPyTZI",
                    "external": False,
                    "users": {},
                    "userGroups": {},
                    "public": "rw------"
                }
            }
            indicators.append(indicator)
            adding_count += 1
    
    # Save
    indicators_data["programIndicators"] = indicators
    with open(indicators_path, "w") as f:
        json.dump(indicators_data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"✓ Created {adding_count} cancer-specific program indicators")
    print(f"  {len(cancer_types)} cancer types × {len(indicator_templates)} indicators per type")
    
    return adding_count

# ============================================================================
# 4. VALIDATION RULES
# ============================================================================

def create_validation_rules():
    """Create essential validation rules for data quality"""
    val_path = BASE_DIR / "Validaion" / "Validation Rule.json"
    
    with open(val_path) as f:
        validation_data = json.load(f)
    
    rules = validation_data.get("validationRules", [])
    
    # New validation rules
    new_rules = [
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Treatment start after diagnosis",
            "description": "Ensures Date of Treatment is after Date of Diagnosis",
            "instruction": "Check that treatment onset is chronologically after diagnosis date",
            "importance": "HIGH",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Valid ECOG performance status",
            "description": "Performance Status must be between 0 and 4",
            "instruction": "Enter ECOG performance status: 0=fully active, 1=restricted, 2=>50% bedbound, 3=bedbound, 4=bedbound 100%",
            "importance": "MEDIUM",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Diagnosis documented before treatment",
            "description": "Cancer Diagnosis field must be populated before treatment can be marked as started",
            "instruction": "Enter cancer diagnosis in ICD-10 code before documenting treatment",
            "importance": "HIGH",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Death date after diagnosis",
            "description": "If patient is deceased, Date of Death must be after Date of Diagnosis",
            "instruction": "Check chronological order of diagnosis and death dates",
            "importance": "HIGH",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Deceased status consistency",
            "description": "If Survival Status = Deceased, then Date of Death must be populated",
            "instruction": "Enter Date of Death if patient status is marked as Deceased",
            "importance": "HIGH",
            "skipFormValidation": False
        },
        {
            "id": generate_uid(),
            "created": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "name": "Treatment response after treatment",
            "description": "Treatment Response should only be assessed after treatment is completed",
            "instruction": "Complete treatment plan and set completion date before assessing response",
            "importance": "MEDIUM",
            "skipFormValidation": False
        }
    ]
    
    rules.extend(new_rules)
    
    validation_data["validationRules"] = rules
    with open(val_path, "w") as f:
        json.dump(validation_data, f, indent=2, ensure_ascii=True)
        f.write("\n")
    
    print(f"✓ Created {len(new_rules)} essential validation rules")
    print(f"  Total validation rules: {len(rules)}")
    
    return len(new_rules)

# ============================================================================

def main():
    print("=" * 80)
    print("CANCER REGISTRY IMPROVEMENTS - PART 2: Datasets, Indicators & Validation")
    print("=" * 80)
    
    print("\n2. IMPROVING DATASETS")
    print("-" * 80)
    ds_count = improve_datasets()
    
    print("\n3. CREATING CANCER-SPECIFIC INDICATORS")
    print("-" * 80)
    ind_count = create_cancer_indicators()
    
    print("\n4. CREATING VALIDATION RULES")
    print("-" * 80)
    val_count = create_validation_rules()
    
    print("\n" + "=" * 80)
    print("IMPROVEMENTS COMPLETED")
    print("=" * 80)
    print(f"✅ Dataset: {ds_count} dataset(s) improved")
    print(f"✅ Indicators: {ind_count} new cancer-specific indicators created")
    print(f"✅ Validation Rules: {val_count} new validation rules created")
    print("=" * 80)

if __name__ == "__main__":
    main()
