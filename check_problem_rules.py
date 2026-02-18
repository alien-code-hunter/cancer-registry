import json

bundle = json.load(open('programs_bundle_cancer.json'))
actions = bundle.get('programRuleActions', [])
variables = bundle.get('programRuleVariables', [])

# Find actions and variables for the problematic rules
problem_rule_ids = {'CqzE5oOx1iU', 'OjEkm0XCaKC'}

problem_actions = [a for a in actions if a.get('programRule', {}).get('id') in problem_rule_ids]
problem_vars = [v for v in variables if v.get('programRule', {}).get('id') in problem_rule_ids]

print(f"Actions for problematic rules: {len(problem_actions)}")
for action in problem_actions:
    de = action.get('dataElement', {}).get('id')
    print(f"  DataElement: {de}")

print(f"\nVariables for problematic rules: {len(problem_vars)}")
for var in problem_vars:
    de = var.get('dataElement', {}).get('id')
    print(f"  DataElement: {de}")
