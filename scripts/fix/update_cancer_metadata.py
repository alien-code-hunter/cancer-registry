import os
import json
from glob import glob

# Path constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRAM_DIR = os.path.join(BASE_DIR, "Program")

# Cancer-specific program files
CANCER_PROGRAM_FILES = glob(os.path.join(PROGRAM_DIR, "Program_*.json"))
GENERIC_STAGE_FILE = os.path.join(PROGRAM_DIR, "Program_Stage_Generic.json")

# Example: CECAP logic templates (to be expanded as needed)
CECAP_RULES = {
    "hiv_status": {
        "label": "HIV Status at screening",
        "options": ["HIV Positive", "HIV Negative", "Unknown"],
        "conditional_fields": [
            {
                "if": "Unknown",
                "show": ["PITC accepted", "Reason PITC not accepted", "PITC results"]
            }
        ]
    },
    "surgical_history": {
        "label": "Gynecological surgical history",
        "options": ["Yes", "No"],
        "conditional_fields": [
            {
                "if": "Yes",
                "show": ["Specify gynecological surgical history"]
            }
        ]
    },
    "image_upload": {
        "label": "Patient scan results",
        "type": "IMAGE"
    }
}

# Cancer-specific exclusions (example, to be expanded)
CANCER_EXCLUSIONS = {
    "Kaposi": ["VIA screening", "Positive margin specification"],
    # Add more as needed
}

# Logical groupings (example, to be expanded)
GROUPS = {
    "HIV": ["HIV Status at screening", "PITC accepted", "PITC results", "ART site", "ART number", "ART start date"],
    "Surgical History": ["Gynecological surgical history", "Specify gynecological surgical history"],
    # Add more as needed
}

def update_program_metadata():
    for program_file in CANCER_PROGRAM_FILES:
        with open(program_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        program_name = os.path.basename(program_file).replace("Program_", "").replace(".json", "")

        # 1. Add CECAP-style rules/logic
        # (This is a placeholder: actual implementation would inspect and update program rules, data elements, etc.)
        # 2. Remove irrelevant elements
        exclusions = CANCER_EXCLUSIONS.get(program_name, [])
        if "programStages" in data:
            for stage in data["programStages"]:
                if "programStageDataElements" in stage:
                    stage["programStageDataElements"] = [
                        de for de in stage["programStageDataElements"]
                        if de.get("dataElement", {}).get("name") not in exclusions
                    ]
        # 3. Group elements (add group info as a new property for now)
        for group, elements in GROUPS.items():
            for stage in data.get("programStages", []):
                for de in stage.get("programStageDataElements", []):
                    if de.get("dataElement", {}).get("name") in elements:
                        de["group"] = group
        # 4. Write back
        with open(program_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    print("Metadata update complete. Please review changes and re-import.")

if __name__ == "__main__":
    update_program_metadata()
