import json
from pathlib import Path

base = Path(__file__).resolve().parents[1]
program_dir = base / "Program"
program_rule_dir = base / "Program Rule"

paths = [
    program_dir / "Program.json",
    program_dir / "Program Stage.json",
    program_dir / "Program Stage Selection.json",
    program_dir / "Program Selection.json",
    program_dir / "Program Indicator Group.json",
    program_dir / "Program Indicator.json",
    program_rule_dir / "Program Rule Variable.json",
    program_rule_dir / "Program Rule.json",
    program_rule_dir / "Program Rule Action.json",
]
paths.extend(sorted(program_dir.glob("*Cancer Program.json")))

combined = {}
for path in paths:
    data = json.loads(path.read_text())
    if not combined and "system" in data:
        combined["system"] = data["system"]
    for key, value in data.items():
        if key == "system":
            continue
        if isinstance(value, list):
            combined.setdefault(key, []).extend(value)
        else:
            combined.setdefault(key, value)

out_path = base / "programs_bundle_full.json"
out_path.write_text(json.dumps(combined, separators=(",", ":")))

counts = {k: len(v) for k, v in combined.items() if isinstance(v, list)}
print(f"Wrote {out_path}")
for key in sorted(counts):
    print(f"{key}: {counts[key]}")
