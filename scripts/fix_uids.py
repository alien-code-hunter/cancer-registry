import json
import random
import string
from pathlib import Path

random.seed()

letters = string.ascii_letters
alphanum = string.ascii_letters + string.digits


def gen_uid(existing):
    while True:
        uid = random.choice(letters) + "".join(random.choice(alphanum) for _ in range(10))
        if uid not in existing:
            existing.add(uid)
            return uid


base = Path(__file__).resolve().parents[1]
program_dir = base / "Program"
program_files = sorted(program_dir.glob("*Cancer Program.json"))

existing_new_ids = set()
new_stages = []

for path in program_files:
    data = json.loads(path.read_text())
    program = data["programs"][0]

    new_program_id = gen_uid(existing_new_ids)
    program["id"] = new_program_id

    for pta in program.get("programTrackedEntityAttributes", []):
        if "id" in pta:
            pta["id"] = gen_uid(existing_new_ids)
        if "program" in pta and isinstance(pta["program"], dict):
            pta["program"]["id"] = new_program_id

    program_short_name = program.get("shortName") or program.get("name") or "Program"
    stages = program.get("programStages", [])
    for idx, stage_ref in enumerate(stages, start=1):
        old_stage_id = stage_ref.get("id", "")
        new_stage_id = gen_uid(existing_new_ids)
        stage_ref["id"] = new_stage_id

        stage_name = "Stage"
        token = old_stage_id.lower()
        if "screen" in token or "scrn" in token:
            stage_name = "Screening"
        elif "diagn" in token or "diag" in token:
            stage_name = "Diagnosis"
        elif "treat" in token:
            stage_name = "Treatment"
        elif "follow" in token or "follw" in token:
            stage_name = "Follow-up"

        new_stages.append(
            {
                "name": f"{program_short_name} {stage_name}",
                "created": program.get("created"),
                "lastUpdated": program.get("lastUpdated"),
                "translations": [],
                "createdBy": program.get("createdBy"),
                "lastUpdatedBy": program.get("lastUpdatedBy"),
                "sharing": program.get("sharing"),
                "minDaysFromStart": 0,
                "program": {"id": new_program_id},
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
                "id": new_stage_id,
                "attributeValues": [],
                "programStageSections": [],
                "notificationTemplates": [],
            }
        )

    path.write_text(json.dumps(data, separators=(",", ":")))

program_stage_path = program_dir / "Program Stage.json"
program_stage_data = json.loads(program_stage_path.read_text())
program_stage_data["programStages"].extend(new_stages)
program_stage_path.write_text(json.dumps(program_stage_data, separators=(",", ":")))

print(f"Updated {len(program_files)} program files.")
print(f"Added {len(new_stages)} program stages.")
