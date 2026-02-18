#!/usr/bin/env python3
"""
Consolidate all cancer programs from individual files into Program.json
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PROGRAM_DIR = BASE_DIR / "archive" / "programs"
PROGRAM_JSON = BASE_DIR / "Program" / "Program.json"

# Load all individual cancer program files
cancer_programs = []
program_files = [
    "Bladder Cancer Program.json",
    "Breast Cancer Program.json",
    "Colorectal Cancer Program.json",
    "Esophageal Cancer Program.json",
    "Kaposi Sarcoma Cancer Program.json",
    "Kidney Cancer Program.json",
    "Leukemia Cancer Program.json",
    "Liver Cancer Program.json",
    "Lung Cancer Program.json",
    "Lymphoma Cancer Program.json",
    "Oral Head Neck Cancer Program.json",
    "Ovarian Cancer Program.json",
    "Pancreatic Cancer Program.json",
    "Prostate Cancer Program.json",
    "Skin Melanoma Cancer Program.json",
    "Stomach Cancer Program.json",
    "Testicular Cancer Program.json",
    "Thyroid Cancer Program.json",
]

print("=" * 80)
print("CONSOLIDATING CANCER PROGRAMS")
print("=" * 80)

for filename in program_files:
    filepath = PROGRAM_DIR / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        programs = data.get('programs', [])
        if programs:
            cancer_programs.extend(programs)
            print(f"✅ {filename}: {len(programs)} program(s) loaded")
    else:
        print(f"⚠️  {filename}: NOT FOUND")

# Load existing Program.json to get the Cervical Cancer Program
with open(PROGRAM_JSON, 'r') as f:
    existing_data = json.load(f)

cervical_programs = existing_data.get('programs', [])
print(f"\nExisting Program.json: {len(cervical_programs)} program(s)")

# Combine all programs
all_programs = cervical_programs + cancer_programs
print(f"\n✅ Total programs to save: {len(all_programs)}")

# Create consolidated Program.json
consolidated_data = {
    "system": existing_data.get("system"),
    "programs": all_programs
}

# Save consolidated Program.json
with open(PROGRAM_JSON, 'w') as f:
    json.dump(consolidated_data, f, indent=2, ensure_ascii=True)
    f.write('\n')

print(f"\n✅ Consolidated Program.json saved with {len(all_programs)} programs")
print("=" * 80)
