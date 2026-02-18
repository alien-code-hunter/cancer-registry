import json
from pathlib import Path

base = Path(__file__).resolve().parents[1]
program_dir = base / "Program"

program_stage_path = program_dir / "Program Stage.json"
program_files = list(program_dir.glob("*Cancer Program.json"))

program_stage_data = json.loads(program_stage_path.read_text())
valid_program_ids = set()

for path in program_files:
    data = json.loads(path.read_text())
    program = data.get("programs", [None])[0]
    if program and "id" in program:
        valid_program_ids.add(program["id"])

kept = []
removed = 0
for stage in program_stage_data.get("programStages", []):
    program_id = stage.get("program", {}).get("id")
    if program_id in valid_program_ids:
        kept.append(stage)
    else:
        removed += 1

program_stage_data["programStages"] = kept
program_stage_path.write_text(json.dumps(program_stage_data, separators=(",", ":")))

print(f"Kept {len(kept)} stages, removed {removed}.")
