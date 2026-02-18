#!/usr/bin/env python3
import json

# Load indicators
with open('Program/Program Indicator.json') as f:
    data = json.load(f)

indicators = data.get('programIndicators', [])

# Fix shortNames to be unique
seen = set()
for ind in indicators:
    name = ind.get('name', '')
    uid = ind.get('id', '')
    
    # Create unique shortName by combining cancer type, feature, and UID suffix
    if ' - ' in name:
        parts = name.split(' - ')
        cancer_type = parts[0][:3]
        feature = parts[1][:6] if len(parts) > 1 else ''
        short_name = f"{cancer_type}-{feature}-{uid[-2:]}".replace(' ', '')
    else:
        short_name = uid[:20]
    
    # Ensure uniqueness
    counter = 1
    orig_short = short_name
    while short_name in seen:
        short_name = f"{orig_short}-{counter}"
        counter += 1
    
    seen.add(short_name)
    ind['shortName'] = short_name[:50]

# Save
with open('Program/Program Indicator.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=True)
    f.write('\n')

print(f"✅ Fixed shortNames for {len(indicators)} indicators")
print(f"   All shortNames are now unique")
