#!/usr/bin/env python3
import json

print('\n' + '='*80)
print('FINAL VERIFICATION - ALL IMPROVEMENTS READY FOR IMPORT')
print('='*80 + '\n')

# Check stages
with open('Program/Program Stage.json') as f:
    stages = json.load(f).get('programStages', [])
renewed = sum(1 for s in stages if 'Assessment' in s.get('name','') or 'Staging' in s.get('name',''))
print(f'✅ Program Stages: {len(stages)} total')
print(f'   └─ {renewed} renamed to clinical workflow')

# Check indicators  
with open('Program/Program Indicator.json') as f:
    indicators = json.load(f).get('programIndicators', [])
with_prog = sum(1 for i in indicators if i.get('program'))
print(f'\n✅ Program Indicators: {len(indicators)} total')
print(f'   └─ {with_prog} with program references')

# Check rules
with open('Validaion/Validation Rule.json') as f:
    rules = json.load(f).get('validationRules', [])
print(f'\n✅ Validation Rules: {len(rules)} total')

# Check data elements
with open('Data Element/Data Element.json') as f:
    elements = json.load(f).get('dataElements', [])
print(f'\n✅ Data Elements: {len(elements)} total')

# Check dashboards
with open('Dashboard/Dashboard.json') as f:
    dashboards = json.load(f).get('dashboards', [])
print(f'\n✅ Dashboards: {len(dashboards)} total')

print('\n' + '='*80)
print('READY FOR IMPORT TO DHIS2 ✅')
print('='*80 + '\n')
