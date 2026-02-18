import json
from pathlib import Path

base = Path(__file__).resolve().parents[1]
program_dir = base / "Program"

program_stage_path = program_dir / "Program Stage.json"
program_path = program_dir / "Program.json"
program_files = sorted(program_dir.glob("*Cancer Program.json"))

program_stage_data = json.loads(program_stage_path.read_text())
program_data = json.loads(program_path.read_text())

keep_program_ids = {p["id"] for p in program_data.get("programs", [])}

kept_stages = []
for stage in program_stage_data.get("programStages", []):
    program_id = stage.get("program", {}).get("id")
    if program_id in keep_program_ids:
        kept_stages.append(stage)

cancer_stages = []

for path in program_files:
    data = json.loads(path.read_text())
    program = data["programs"][0]
    program_id = program["id"]
    short_name = program.get("shortName") or program.get("name") or "Program"

    for idx, stage_ref in enumerate(program.get("programStages", []), start=1):
        stage_id = stage_ref.get("id")
        if not stage_id:
            continue

        old_stage_id = stage_ref.get("id", "")
        token = old_stage_id.lower()
        if "screen" in token or "scrn" in token:
            stage_name = "Screening"
        elif "diagn" in token or "diag" in token:
            stage_name = "Diagnosis"
        elif "treat" in token:
            stage_name = "Treatment"
        elif "follow" in token or "follw" in token:
            stage_name = "Follow-up"
        else:
            stage_name = "Stage"

        cancer_stages.append(
            {
                "name": f"{short_name} {stage_name}",
                "created": program.get("created"),
                "lastUpdated": program.get("lastUpdated"),
                "translations": [],
                "createdBy": program.get("createdBy"),
                "lastUpdatedBy": program.get("lastUpdatedBy"),
                "sharing": program.get("sharing"),
                "minDaysFromStart": 0,
                "program": {"id": program_id},
                "programStageDataElements": [],
                "executionDateLabel": "Visit date",
                "autoGenerateEvent": False,
                "validationStrategy": "ON_COMPLETE",
                "displayGenerateEventBox": False,
                "blockEntryForm": False,
                "preGenerateUID": False,
                "remindCompleted": False,
                "generatedByEnrollmentDate": False,
                "allowGenerateNextVisit": False,
                "openAfterEnrollment": False,
                "sortOrder": idx,
                "hideDueDate": True,
                "enableUserAssignment": False,
                "referral": False,
                "repeatable": True,
                "id": stage_id,
                "attributeValues": [],
                "programStageSections": [],
                "notificationTemplates": [],
            }
        )

program_stage_data["programStages"] = kept_stages + cancer_stages
program_stage_path.write_text(json.dumps(program_stage_data, separators=(",", ":")))

print(f"Kept {len(kept_stages)} existing stages.")
print(f"Added {len(cancer_stages)} cancer stages.")
