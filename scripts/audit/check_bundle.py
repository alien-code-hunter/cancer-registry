import json

# Load the bundle
bundle = json.load(open('programs_bundle_cancer.json'))
rules = bundle.get('programRules', [])
actions = bundle.get('programRuleActions', [])
variables = bundle.get('programRuleVariables', [])

# Find the rule about 'HIDE: Biopsy performed'
matching_rules = [r for r in rules if 'Biopsy' in r.get('name', '') or 'biopsy' in r.get('name', '').lower()]
print(f'Found {len(matching_rules)} rules mentioning biopsy')

for rule in matching_rules[:5]:
    rule_name = rule.get('name')
    rule_id = rule.get('id')
    program_id = rule.get('program', {}).get('id')
    stage_id = rule.get('programStage', {}).get('id')
    
    print(f'\nRule: {rule_name} (id: {rule_id})')
    print(f'  Program: {program_id}')
    print(f'  Stage: {stage_id}')
    
    # Find related actions
    rule_actions = [a for a in actions if a.get('programRule', {}).get('id') == rule_id]
    print(f'  Actions: {len(rule_actions)}')
    for action in rule_actions:
        de = action.get('dataElement', {}).get('id')
        print(f'    - Action DataElement: {de}')
    
    # Find related variables
    rule_vars = [v for v in variables if v.get('programRule', {}).get('id') == rule_id]
    print(f'  Variables: {len(rule_vars)}')
    for var in rule_vars:
        de = var.get('dataElement', {}).get('id')
        print(f'    - Variable DataElement: {de}')

# Now specifically check for AswNlG485pW
print('\n\n--- Checking for AswNlG485pW ---')
matching_actions = [a for a in actions if a.get('dataElement', {}).get('id') == 'AswNlG485pW']
print(f'Found {len(matching_actions)} actions using AswNlG485pW')
for action in matching_actions:
    rule_id = action.get('programRule', {}).get('id')
    rule = next((r for r in rules if r.get('id') == rule_id), None)
    if rule:
        print(f'  Rule: {rule.get("name")} (stage: {rule.get("programStage", {}).get("id")})')
