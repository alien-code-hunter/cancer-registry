import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PROGRAM_STAGE_PATH = BASE_DIR / "Program" / "Program Stage.json"
PROGRAM_RULE_VARIABLE_PATH = BASE_DIR / "Program Rule" / "Program Rule Variable.json"
PROGRAM_RULE_ACTION_PATH = BASE_DIR / "Program Rule" / "Program Rule Action.json"
PROGRAM_RULE_PATH = BASE_DIR / "Program Rule" / "Program Rule.json"
PROGRAM_STAGE_SELECTION_PATH = BASE_DIR / "Program" / "Program Stage Selection.json"

CECAP_PROGRAM_ID = "F5lx6p0yaU9"
CECAP_STAGE_DEFINITIONS = {
    "ymx76J82mIm": {"name": "CECAP Screening", "sortOrder": 1},
    "CAiHMH7NGaj": {"name": "CECAP Treatment", "sortOrder": 2},
    "Lzn5PoFfmr8": {"name": "CECAP Lab", "sortOrder": 3},
}


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    program_stages_data = load_json(PROGRAM_STAGE_PATH)
    program_rules_data = load_json(PROGRAM_RULE_PATH)
    rule_actions_data = load_json(PROGRAM_RULE_ACTION_PATH)
    rule_variables_data = load_json(PROGRAM_RULE_VARIABLE_PATH)
    stage_sections_data = load_json(PROGRAM_STAGE_SELECTION_PATH)

    program_stages = program_stages_data.get("programStages", [])
    existing_stage_ids = {stage.get("id") for stage in program_stages if stage.get("id")}

    if program_stages:
        template = program_stages[0]
        added_stages = 0
        for stage_id, info in CECAP_STAGE_DEFINITIONS.items():
            if stage_id in existing_stage_ids:
                continue
            new_stage = {
                "name": info["name"],
                "created": template.get("created"),
                "lastUpdated": template.get("lastUpdated"),
                "translations": [],
                "createdBy": template.get("createdBy"),
                "lastUpdatedBy": template.get("lastUpdatedBy"),
                "sharing": template.get("sharing"),
                "minDaysFromStart": template.get("minDaysFromStart", 0),
                "program": {"id": CECAP_PROGRAM_ID},
                "programStageDataElements": [],
                "executionDateLabel": template.get("executionDateLabel", "Visit date"),
                "autoGenerateEvent": template.get("autoGenerateEvent", False),
                "validationStrategy": template.get("validationStrategy", "ON_COMPLETE"),
                "displayGenerateEventBox": template.get("displayGenerateEventBox", False),
                "blockEntryForm": template.get("blockEntryForm", False),
                "preGenerateUID": template.get("preGenerateUID", False),
                "remindCompleted": template.get("remindCompleted", False),
                "generatedByEnrollmentDate": template.get("generatedByEnrollmentDate", False),
                "allowGenerateNextVisit": template.get("allowGenerateNextVisit", False),
                "openAfterEnrollment": template.get("openAfterEnrollment", False),
                "sortOrder": info["sortOrder"],
                "hideDueDate": template.get("hideDueDate", True),
                "enableUserAssignment": template.get("enableUserAssignment", False),
                "referral": template.get("referral", False),
                "repeatable": template.get("repeatable", True),
                "id": stage_id,
                "attributeValues": [],
                "programStageSections": [],
                "notificationTemplates": [],
            }
            program_stages.append(new_stage)
            added_stages += 1
        if added_stages:
            program_stages_data["programStages"] = program_stages

    rule_to_stage = {}
    for rule in program_rules_data.get("programRules", []):
        rule_id = rule.get("id")
        stage = rule.get("programStage", {})
        stage_id = stage.get("id") if isinstance(stage, dict) else None
        if rule_id and stage_id:
            rule_to_stage[rule_id] = stage_id

    stage_to_elements = defaultdict(list)
    stage_to_elements_set = defaultdict(set)

    def add_element(stage_id, data_element_id):
        if not stage_id or not data_element_id:
            return
        if data_element_id in stage_to_elements_set[stage_id]:
            return
        stage_to_elements_set[stage_id].add(data_element_id)
        stage_to_elements[stage_id].append(data_element_id)

    for section in stage_sections_data.get("programStageSections", []):
        stage = section.get("programStage", {})
        stage_id = stage.get("id") if isinstance(stage, dict) else None
        for element in section.get("dataElements", []):
            element_id = element.get("id") if isinstance(element, dict) else None
            add_element(stage_id, element_id)

    for variable in rule_variables_data.get("programRuleVariables", []):
        stage = variable.get("programStage", {})
        stage_id = stage.get("id") if isinstance(stage, dict) else None
        data_element = variable.get("dataElement", {})
        data_element_id = data_element.get("id") if isinstance(data_element, dict) else None
        add_element(stage_id, data_element_id)

    for action in rule_actions_data.get("programRuleActions", []):
        rule = action.get("programRule", {})
        rule_id = rule.get("id") if isinstance(rule, dict) else None
        stage_id = rule_to_stage.get(rule_id)
        data_element = action.get("dataElement", {})
        data_element_id = data_element.get("id") if isinstance(data_element, dict) else None
        add_element(stage_id, data_element_id)

    updated_count = 0
    for stage in program_stages_data.get("programStages", []):
        stage_id = stage.get("id")
        if not stage_id:
            continue
        elements = stage_to_elements.get(stage_id)
        if not elements:
            continue

        existing = stage.get("programStageDataElements") or []
        existing_ids = {
            item.get("dataElement", {}).get("id")
            for item in existing
            if isinstance(item, dict)
        }

        new_ids = [elem_id for elem_id in elements if elem_id not in existing_ids]
        if not new_ids:
            continue

        sort_order_start = len(existing) + 1
        for offset, elem_id in enumerate(new_ids):
            existing.append(
                {
                    "dataElement": {"id": elem_id},
                    "compulsory": False,
                    "allowProvidedElsewhere": False,
                    "allowFutureDate": False,
                    "sortOrder": sort_order_start + offset,
                }
            )

        stage["programStageDataElements"] = existing
        updated_count += 1

    with PROGRAM_STAGE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(program_stages_data, handle, indent=2, ensure_ascii=True)
        handle.write("\n")

    print(f"Updated {updated_count} program stages with programStageDataElements.")


if __name__ == "__main__":
    main()
