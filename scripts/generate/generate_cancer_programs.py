"""
Cancer Program Generator

Generates one JSON file per cancer (excluding Cervical) with:
- Standardized program stages
- Stage-to-data-element mapping
- Core and cancer-specific data elements
- Rule definitions (as structured specs)

Place this script in scripts/generate/generate_cancer_programs.py
"""
import json
import os

# --- CONFIG ---
CANCERS = [
    "Bladder", "Breast", "Colorectal", "Esophageal", "Kaposi", "Kidney", "Leukemia", "Liver", "Lung", "Lymphoma", "Melanoma", "Oral", "Ovarian", "Pancreatic", "Prostate", "Stomach", "Testicular", "Thyroid"
]

# Shared core data elements (abbreviated for brevity)
CORE_ELEMENTS = [
    {"name": "National ID", "id": "core_national_id", "valueType": "TEXT"},
    {"name": "Full name", "id": "core_full_name", "valueType": "TEXT"},
    {"name": "DOB", "id": "core_dob", "valueType": "DATE"},
    {"name": "Sex", "id": "core_sex", "valueType": "TEXT"},
    {"name": "Phone", "id": "core_phone", "valueType": "TEXT"},
    {"name": "Address", "id": "core_address", "valueType": "TEXT"},
    {"name": "Registry Case ID", "id": "core_case_id", "valueType": "TEXT"},
    {"name": "Encounter date", "id": "core_encounter_date", "valueType": "DATE"},
    {"name": "HIV status", "id": "core_hiv_status", "valueType": "TEXT"},
    {"name": "Smoking status", "id": "core_smoking_status", "valueType": "TEXT"},
    {"name": "Alcohol use", "id": "core_alcohol_use", "valueType": "TEXT"},
    {"name": "Family history of cancer", "id": "core_family_history", "valueType": "TEXT"},
    {"name": "Comorbidities", "id": "core_comorbidities", "valueType": "TEXT"},
    {"name": "Primary cancer site", "id": "core_primary_site", "valueType": "TEXT"},
    {"name": "Date of diagnosis", "id": "core_diag_date", "valueType": "DATE"},
    {"name": "Basis of diagnosis", "id": "core_basis_diag", "valueType": "TEXT"},
    {"name": "Histology type", "id": "core_histology", "valueType": "TEXT"},
    {"name": "Grade", "id": "core_grade", "valueType": "NUMBER"},
    {"name": "ICD-10 code", "id": "core_icd10", "valueType": "TEXT"},
    {"name": "Staging system", "id": "core_staging_system", "valueType": "TEXT"},
    {"name": "Stage group", "id": "core_stage_group", "valueType": "TEXT"},
    {"name": "T", "id": "core_t", "valueType": "TEXT"},
    {"name": "N", "id": "core_n", "valueType": "TEXT"},
    {"name": "M", "id": "core_m", "valueType": "TEXT"},
    {"name": "Performance status", "id": "core_perf_status", "valueType": "NUMBER"},
    {"name": "Treatment intent", "id": "core_treatment_intent", "valueType": "TEXT"},
    {"name": "Surgery done", "id": "core_surgery_done", "valueType": "BOOLEAN"},
    {"name": "Chemo started", "id": "core_chemo_started", "valueType": "BOOLEAN"},
    {"name": "Radiotherapy started", "id": "core_rt_started", "valueType": "BOOLEAN"},
    {"name": "Hormonal therapy", "id": "core_hormonal", "valueType": "BOOLEAN"},
    {"name": "Targeted/immunotherapy", "id": "core_targeted", "valueType": "BOOLEAN"},
    {"name": "Treatment completion status", "id": "core_treatment_status", "valueType": "TEXT"},
    {"name": "Vital status", "id": "core_vital_status", "valueType": "TEXT"},
    {"name": "Date last seen", "id": "core_last_seen", "valueType": "DATE"},
    {"name": "Disease status", "id": "core_disease_status", "valueType": "TEXT"},
    {"name": "Recurrence", "id": "core_recurrence", "valueType": "BOOLEAN"},
    {"name": "Palliative care enrolled", "id": "core_palliative", "valueType": "BOOLEAN"},
    {"name": "Death details", "id": "core_death_details", "valueType": "TEXT"}
]


# Cancer-specific elements mapped to stages (expanded for all cancers as needed)
CANCER_STAGE_ELEMENTS = {
    "Bladder": {
        "Diagnostics": [
            {"name": "Cystoscopy findings", "id": "bladder_cystoscopy", "valueType": "TEXT"},
            {"name": "Urine cytology", "id": "bladder_urine_cytology", "valueType": "TEXT"},
            {"name": "Imaging study", "id": "bladder_imaging", "valueType": "TEXT"},
            {"name": "Biopsy (TURBT)", "id": "bladder_biopsy_turbt", "valueType": "TEXT"},
            {"name": "Blue light cystoscopy", "id": "bladder_blue_light", "valueType": "TEXT"}
        ],
        "Staging": [
            {"name": "Muscle invasion", "id": "bladder_muscle_invasion", "valueType": "BOOLEAN"},
            {"name": "Tumour size", "id": "bladder_tumour_size", "valueType": "NUMBER"}
        ],
        "Treatment Delivery": [
            {"name": "Treatment type", "id": "bladder_treatment_type", "valueType": "TEXT"},
            {"name": "Complications", "id": "bladder_treatment_complications", "valueType": "TEXT"}
        ],
        "Follow-up / Response": [
            {"name": "Recurrence event", "id": "bladder_recurrence_event", "valueType": "BOOLEAN"}
        ]
    },
    # Add other cancers with their own stage-to-element mapping as needed...
}

# Standard program stages
STAGES = [
    "Registration & Risk",
    "Clinical Assessment",
    "Diagnostics",
    "Staging",
    "MDT & Treatment Plan",
    "Treatment Delivery",
    "Follow-up / Response",
    "Outcome / Death"
]

# Example rule spec (abbreviated)
RULES = [
    {"if": "HIV_status == Positive", "then": ["ART_status mandatory", "On_ART_since show"]},
    {"if": "Biopsy_done == Yes", "then": ["Pathology_result mandatory", "Histology_type mandatory"]},
    {"if": "Imaging_done == Yes", "then": ["Imaging_type show", "Imaging_result_summary show"]},
    {"if": "Stage_group == IV", "then": ["Palliative_care_enrolled show"]},
    {"if": "Sex != Female", "then": ["Hide pregnancy-related elements"]},
    {"if": "Vital_status == Dead", "then": ["Date_of_death mandatory", "Place_of_death mandatory"]}
]

# Output directory
OUT_DIR = os.path.join(os.path.dirname(__file__), '../../Program')
os.makedirs(OUT_DIR, exist_ok=True)


for cancer in CANCERS:
    stage_elements = {}
    for stage in STAGES:
        # Always include only core elements and cancer-specific elements for this stage
        elements = [e for e in CORE_ELEMENTS]  # copy core
        if cancer in CANCER_STAGE_ELEMENTS and stage in CANCER_STAGE_ELEMENTS[cancer]:
            elements += CANCER_STAGE_ELEMENTS[cancer][stage]
        stage_elements[stage] = elements
    program = {
        "name": f"{cancer} Cancer Program",
        "stages": [
            {"name": stage, "dataElements": stage_elements[stage]} for stage in STAGES
        ],
        "rules": RULES
    }
    out_path = os.path.join(OUT_DIR, f"Program_{cancer}.json")
    with open(out_path, 'w') as f:
        json.dump(program, f, indent=2)

print(f"Generated {len(CANCERS)} cancer program files in {OUT_DIR}")
