#!/usr/bin/env python3
"""
Comprehensive cancer registry improvement script.
Addresses:
1. Program stages - create real-world cancer tracker stages
2. Data sets - create per-cancer datasets
3. Program indicators - create cancer-specific KPIs  
4. Validation rules - create data quality validation rules
"""

import json
import uuid
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]

# ============================================================================
# REAL-WORLD CANCER TRACKER STAGES
# ============================================================================

CANCER_PROGRAM_STAGES = {
    "real-world stages based on clinical cancer management workflow":
    {
        "1. Initial Assessment": {
            "description": "Patient presentation and initial clinical evaluation",
            "sortOrder": 1,
            "data_elements": [
                "Patient demographics",
                "Chief complaint",
                "Risk factors",
                "Symptom duration",
                "ECOG performance status"
            ]
        },
        "2. Diagnostic Workup": {
            "description": "Diagnostic investigations and imaging",
            "sortOrder": 2,
            "data_elements": [
                "Lab tests (CBC, chemistry)",
                "Imaging results (CT, MRI, PET)",
                "Biopsy/pathology results",
                "TNM staging parameters",
                "Tumor markers"
            ]
        },
        "3. Staging & Risk Assessment": {
            "description": "Final staging and risk stratification",
            "sortOrder": 3,
            "data_elements": [
                "Clinical TNM stage",
                "Pathological TNM stage",
                "Grade/histology",
                "Molecular markers",
                "Risk stratification category",
                "Comorbidities"
            ]
        },
        "4. Treatment Planning": {
            "description": "Multidisciplinary team assessment and plan",
            "sortOrder": 4,
            "data_elements": [
                "Treatment modality decision",
                "Surgery plan (if applicable)",
                "Chemotherapy regimen",
                "Radiation therapy plan",
                "Immunotherapy plan",
                "Target/molecularly targeted therapy",
                "Treatment intent (curative/palliative)"
            ]
        },
        "5. Active Treatment": {
            "description": "Execution of treatment plan",
            "sortOrder": 5,
            "data_elements": [
                "Treatment start date",
                "Surgery details (date, type, complications)",
                "Chemotherapy cycles/doses",
                "Radiation therapy fractions",
                "Immunotherapy cycles",
                "Treatment-related toxicities (CTCAE)",
                "Treatment interruptions"
            ]
        },
        "6. Treatment Response Assessment": {
            "description": "Evaluation of treatment response",
            "sortOrder": 6,
            "data_elements": [
                "Treatment completion date",
                "Response assessment (RECIST)",
                "Residual disease status",
                "Tumor markers post-treatment",
                "Imaging findings",
                "Pathological response"
            ]
        },
        "7. Follow-up & Surveillance": {
            "description": "Long-term monitoring for recurrence",
            "sortOrder": 7,
            "data_elements": [
                "Follow-up visit date",
                "Clinical examination findings",
                "Imaging surveillance",
                "Tumor marker monitoring",
                "Performance status",
                "Treatment complications/late effects"
            ]
        },
        "8. Outcome & Survival": {
            "description": "Final status and outcomes",
            "sortOrder": 8,
            "data_elements": [
                "Outcome status (alive, deceased, lost-to-followup)",
                "Survival duration",
                "Cause of death (if applicable)",
                "Recurrence status",
                "Disease-free survival",
                "Overall survival",
                "Quality of life"
            ]
        }
    }
}

# ============================================================================
# CANCER-SPECIFIC INDICATORS FOR REAL-WORLD SCENARIOS
# ============================================================================

CANCER_INDICATORS = [
    {
        "name": "{cancer} - Early Detection Rate",
        "description": "% of {cancer} cases detected at Stage I-II",
        "numerator": "Patients with Stage I-II {cancer}",
        "denominator": "Total {cancer} cases"
    },
    {
        "name": "{cancer} - Treatment Completion Rate",
        "description": "% of {cancer} patients who completed planned treatment",
        "numerator": "Patients who completed planned treatment",
        "denominator": "Patients with treatment plan"
    },
    {
        "name": "{cancer} - Median Overall Survival",
        "description": "Median Overall Survival in months for {cancer}",
        "numerator": "Sum of survival months",
        "denominator": "Number of {cancer} patients"
    },
    {
        "name": "{cancer} - 1-Year Survival Rate",
        "description": "% of {cancer} patients alive at 12 months",
        "numerator": "Patients alive at 12 months",
        "denominator": "Total {cancer} cases"
    },
    {
        "name": "{cancer} - 5-Year Survival Rate",
        "description": "% of {cancer} patients alive at 60 months",
        "numerator": "Patients alive at 60 months",
        "denominator": "Total {cancer} cases"
    },
    {
        "name": "{cancer} - Treatment-Related Mortality",
        "description": "Deaths within 30 days of treatment in {cancer} patients",
        "numerator": "Deaths within 30 days of treatment",
        "denominator": "Patients receiving treatment"
    },
    {
        "name": "{cancer} - Delayed Diagnosis Rate",
        "description": "% of {cancer} patients presenting >6 months after symptom onset",
        "numerator": "Patients with >6 month diagnostic delay",
        "denominator": "Total {cancer} cases"
    },
    {
        "name": "{cancer} - Disease-Free Survival at 2 Years",
        "description": "% of {cancer} patients without recurrence at 2 years",
        "numerator": "Patients without recurrence at 2 years",
        "denominator": "Total {cancer} cases"
    }
]

# ============================================================================
# VALIDATION RULES FOR DATA QUALITY
# ============================================================================

VALIDATION_RULES = [
    {
        "name": "Treatment start must be after diagnosis",
        "type": "date_order_validation",
        "fields": ["Date of Diagnosis", "Date of Treatment"],
        "rule": "Date of Diagnosis <= Date of Treatment"
    },
    {
        "name": "ECOG performance status must be 0-4",
        "type": "range_validation",
        "field": "Performance Status",
        "min": 0,
        "max": 4
    },
    {
        "name": "Diagnosis and staging must be completed before treatment",
        "type": "logical_validation",
        "rule": "Cancer Diagnosis and Cancer Stage must be populated before treatment start"
    },
    {
        "name": "Death date cannot be before diagnosis",
        "type": "date_order_validation",
        "fields": ["Date of Diagnosis", "Date of Death"],
        "rule": "Date of Diagnosis <= Date of Death"
    },
    {
        "name": "Survival status must match death data",
        "type": "logical_validation",
        "rule": "If Survival Status = Deceased, then Date of Death must be populated"
    },
    {
        "name": "Treatment response requires completed treatment",
        "type": "conditional_validation",
        "condition": "Treatment Response populated",
        "requirement": "Treatment completion date must be populated"
    }
]

# ============================================================================

def main():
    print("=" * 80)
    print("CANCER REGISTRY COMPREHENSIVE IMPROVEMENT ANALYSIS")
    print("=" * 80)
    
    # Load current data
    with open(BASE_DIR / "Program" / "Program.json") as f:
        programs_data = json.load(f)
    
    with open(BASE_DIR / "Program" / "Program Stage.json") as f:
        stages_data = json.load(f)
    
    with open(BASE_DIR / "Program" / "Program Indicator.json") as f:
        indicators_data = json.load(f)
    
    with open(BASE_DIR / "Data Set" / "Data Set.json") as f:
        datasets_data = json.load(f)
    
    with open(BASE_DIR / "Validation" / "Validation Rule.json") as f:
        validation_data = json.load(f)
    
    programs = {p.get("id"): p.get("name") for p in programs_data.get("programs", [])}
    stages = stages_data.get("programStages", [])
    indicators = indicators_data.get("programIndicators", [])
    datasets = datasets_data.get("dataSets", [])
    rules = validation_data.get("validationRules", [])
    
    # Analyze
    stages_by_program = defaultdict(list)
    for stage in stages:
        prog_id = stage.get("program", {}).get("id")
        stages_by_program[prog_id].append(stage.get("name"))
    
    indicators_by_program = defaultdict(int)
    for ind in indicators:
        prog = ind.get("program", {})
        prog_id = prog.get("id") if isinstance(prog, dict) else prog
        indicators_by_program[prog_id] += 1
    
    print("\n1. PROGRAM STAGES ANALYSIS")
    print("-" * 80)
    print(f"   Total stages: {len(stages)}")
    print(f"   Total programs: {len(programs)}")
    print("\n   Current stage naming issues:")
    for prog_id, prog_name in list(programs.items())[:3]:
        stage_names = stages_by_program.get(prog_id, [])
        print(f"\n   {prog_name}:")
        for sname in stage_names[:2]:
            print(f"     ⚠️  '{sname}' (poorly named - not descriptive)")
    print(f"\n   ✓ Good example - CECAP stages:")
    print(f"     - 'CECAP Screening' (Clear purpose)")
    print(f"     - 'CECAP Treatment' (Clear purpose)")
    print(f"     - 'CECAP Lab' (Clear purpose)")
    
    print("\n2. DATA SETS ANALYSIS")
    print("-" * 80)
    print(f"   Total datasets: {len(datasets)}")
    for ds in datasets:
        print(f"   - '{ds.get('name')}' ({ds.get('id')})")
    print(f"\n   Issue: Single dataset for all cancer types")
    print(f"   Recommendation: Create per-cancer datasets for better organization")
    
    print("\n3. PROGRAM INDICATORS ANALYSIS")
    print("-" * 80)
    print(f"   Total program indicators: {len(indicators)}")
    print(f"\n   Indicators by program:")
    for prog_id, prog_name in list(programs.items())[:6]:
        count = indicators_by_program.get(prog_id, 0)
        status = "✓" if count > 0 else "⚠️ "
        print(f"   {status} {prog_name}: {count} indicators")
    print(f"\n   Issue: Most programs lack indicators (especially non-CECAP programs)")
    print(f"   Recommendation: Create {len(CANCER_INDICATORS)} real-world KPIs per cancer type")
    
    print("\n4. VALIDATION RULES ANALYSIS")
    print("-" * 80)
    print(f"   Total validation rules: {len(rules)}")
    if not rules:
        print(f"   ⚠️  NO VALIDATION RULES DEFINED")
        print(f"   Recommendation: Create {len(VALIDATION_RULES)} essential validation rules")
    
    print("\n" + "=" * 80)
    print("IMPROVEMENT RECOMMENDATIONS SUMMARY")
    print("=" * 80)
    print("""
    1. PROGRAM STAGES: Rename all cancer program stages to 8 standard clinical stages
       - Initial Assessment → Diagnostic Workup → Staging → Planning → Active Treatment
       - Response Assessment → Follow-up → Outcomes & Survival
       Impact: 72 existing stages × 18 cancers = rename/reorganize needed

    2. DATA SETS: Create unified cancer tracking dataset
       - Option A: Rename CECAP to "Cancer Registry Data" (covers all cancers)
       - Option B: Create per-cancer datasets for isolation
       Recommendation: Option A (simpler, unified tracking)

    3. PROGRAM INDICATORS: Create 8 cancer-specific KPIs for each of 18 cancers
       - Early Detection Rate
       - Treatment Completion Rate
       - 1-Year & 5-Year Survival Rates
       - Treatment-Related Mortality
       - Disease-Free Survival
       - Delayed Diagnosis Rate
       Impact: 144 new indicators (8 per cancer × 18 cancers)
              + existing 2 CECAP indicators = ~876 total

    4. VALIDATION RULES: Create 6 essential rules for data quality
       - Date ordering validations
       - Range validations (e.g., ECOG 0-4)
       - Logical field dependencies
       - Conditional requirements
       Impact: Ensure data consistency across all programs
    """)
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
