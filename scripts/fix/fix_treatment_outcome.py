import json

# Path to the generic program stage file
stage_file = "Program/Program_Stage_Generic.json"

# Data element ID for 'Treatment Outcome'
treatment_outcome_id = "QCRq9U2eIYW"

with open(stage_file, "r", encoding="utf-8") as f:
    data = json.load(f)

for stage in data.get("programStages", []):
    # Remove 'Treatment Outcome' from all stages
    stage["programStageDataElements"] = [
        de for de in stage.get("programStageDataElements", [])
        if de.get("dataElement", {}).get("id") != treatment_outcome_id
    ]
    # Add it back only to '3. Active Treatment' if not present
    if stage.get("name") == "3. Active Treatment":
        ids = [de.get("dataElement", {}).get("id") for de in stage.get("programStageDataElements", [])]
        if treatment_outcome_id not in ids:
            stage["programStageDataElements"].append({
                "dataElement": {"id": treatment_outcome_id},
                "compulsory": False,
                "allowProvidedElsewhere": False,
                "allowFutureDate": False,
                "sortOrder": 999
            })

with open(stage_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("'Treatment Outcome' now only appears in '3. Active Treatment' stage.")
