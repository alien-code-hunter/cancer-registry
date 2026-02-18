#!/usr/bin/env python3
"""
Group Data Elements by Cancer Type - Reference File
"""

import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/mk/Documents/GitHub/cancer-registry")
de_path = BASE_DIR / "Data Element" / "Data Element.json"

with open(de_path) as f:
    de_data = json.load(f)

data_elements = de_data.get('dataElements', [])

# Group by cancer type
grouped = defaultdict(list)

for de in data_elements:
    name = de.get('name', '')
    de_id = de.get('id', '')
    
    # Determine cancer type
    cancer_type = 'Generic Cancer'
    
    cancers = ['Breast', 'Prostate', 'Lung', 'Colorectal', 'Kidney', 'Liver',
               'Stomach', 'Pancreatic', 'Ovarian', 'Testicular', 'Bladder',
               'Thyroid', 'Leukemia', 'Lymphoma', 'Oral', 'Esophageal',
               'Kaposi', 'Melanoma', 'Cervical', 'CECAP']
    
    for cancer in cancers:
        if cancer.lower() in name.lower():
            cancer_type = cancer
            break
    
    grouped[cancer_type].append({'id': de_id, 'name': name})

# Create reference file
ref_file = BASE_DIR / "Data Element" / "Data Elements by Cancer Type.json"
reference = {
    'dataElementsByType': dict(grouped),
    'summary': {cancer: len(elements) for cancer, elements in grouped.items()},
    'totalElements': len(data_elements)
}

with open(ref_file, 'w') as f:
    json.dump(reference, f, indent=2, ensure_ascii=True)
    f.write('\n')

print("✅ Created Data Elements by Cancer Type Reference")
print("\nGrouping Summary:")
for cancer in sorted(grouped.keys()):
    print(f"  • {cancer}: {len(grouped[cancer])} elements")
print(f"\nTotal: {len(data_elements)} elements")
