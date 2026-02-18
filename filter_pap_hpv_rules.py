import json
from pathlib import Path

base = Path(__file__).resolve().parents[0]
bundle_path = base / "programs_bundle_cancer.json"

# Load bundle
bundle = json.loads(bundle_path.read_text())

# Filter out any rule containing HPV or Pap smear keywords
original_rules = bundle.get('programRules', [])
filtered_rules = [r for r in original_rules 
                 if not any(keyword in r.get('name', '').upper() 
                           for keyword in ['HPV', 'PAP SMEAR', 'PAP'])]

print(f"Original rules: {len(original_rules)}")
print(f"Filtered rules: {len(filtered_rules)}")
print(f"Removed: {len(original_rules) - len(filtered_rules)}")

removed_rules = [r for r in original_rules 
                if any(keyword in r.get('name', '').upper() 
                      for keyword in ['HPV', 'PAP SMEAR', 'PAP'])]
print("\nRemoved rules:")
for rule in removed_rules:
    print(f"  - {rule.get('name')} (id: {rule.get('id')})")

if len(filtered_rules) < len(original_rules):
    bundle['programRules'] = filtered_rules
    
    # Remove associated actions for these rules
    removed_rule_ids = {r.get('id') for r in removed_rules}
    original_actions = bundle.get('programRuleActions', [])
    filtered_actions = [a for a in original_actions 
                       if a.get('programRule', {}).get('id') not in removed_rule_ids]
    
    # Remove associated variables for these rules
    original_vars = bundle.get('programRuleVariables', [])
    filtered_vars = [v for v in original_vars 
                    if v.get('programRule', {}).get('id') not in removed_rule_ids]
    
    print(f"\nOriginal actions: {len(original_actions)}")
    print(f"Filtered actions: {len(filtered_actions)}")
    print(f"Removed actions: {len(original_actions) - len(filtered_actions)}")
    
    print(f"\nOriginal variables: {len(original_vars)}")
    print(f"Filtered variables: {len(filtered_vars)}")
    print(f"Removed variables: {len(original_vars) - len(filtered_vars)}")
    
    bundle['programRuleActions'] = filtered_actions
    bundle['programRuleVariables'] = filtered_vars
    
    # Save filtered bundle
    out_path = base / "programs_bundle_cancer_no_pap_hpv.json"
    out_path.write_text(json.dumps(bundle, separators=(",", ":")))
    print(f"\nWrote filtered bundle to {out_path.name}")
else:
    print("\nNo rules were removed")
