import json
from pathlib import Path

base = Path(__file__).resolve().parents[0]
bundle_path = base / "programs_bundle_cancer.json"

# Load bundle
bundle = json.loads(bundle_path.read_text())

# Filter out the Pap smear and HPV rules that are causing issues
problem_rule_ids = {
    'CqzE5oOx1iU',  # HIDE: HPV DNA Test Results details
    'OjEkm0XCaKC',  # HIDE: Pap smear screening type
}

original_rules = bundle.get('programRules', [])
filtered_rules = [r for r in original_rules if r.get('id') not in problem_rule_ids]

print(f"Original rules: {len(original_rules)}")
print(f"Filtered rules: {len(filtered_rules)}")
print(f"Removed: {len(original_rules) - len(filtered_rules)}")

if len(filtered_rules) < len(original_rules):
    bundle['programRules'] = filtered_rules
    
    # Also remove associated actions for these rules
    original_actions = bundle.get('programRuleActions', [])
    filtered_actions = [a for a in original_actions 
                       if a.get('programRule', {}).get('id') not in problem_rule_ids]
    
    print(f"Original actions: {len(original_actions)}")
    print(f"Filtered actions: {len(filtered_actions)}")
    
    bundle['programRuleActions'] = filtered_actions
    
    # Save filtered bundle
    out_path = base / "programs_bundle_cancer_filtered.json"
    out_path.write_text(json.dumps(bundle, separators=(",", ":")))
    print(f"\nWrote filtered bundle to {out_path.name}")
else:
    print("No rules were removed")
