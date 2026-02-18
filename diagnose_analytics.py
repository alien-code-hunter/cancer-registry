#!/usr/bin/env python3
"""
Validate program indicators and find analytics issues
"""
import json
import re

print("=" * 80)
print("ANALYTICS ISSUE INVESTIGATION")
print("=" * 80)

# Load all data
with open('Program/Program Indicator.json') as f:
    pi_data = json.load(f)
indicators = pi_data.get('programIndicators', [])

with open('Program/Program.json') as f:
    prog_data = json.load(f)
programs = prog_data.get('programs', [])
program_ids = {p.get('id') for p in programs}

with open('Data Element/Data Element.json') as f:
    de_data = json.load(f)
de_ids = {de.get('id') for de in de_data.get('dataElements', [])}

print(f"\n📊 Data Summary:")
print(f"   Program Indicators: {len(indicators)}")
print(f"   Programs: {len(programs)}")
print(f"   Data Elements: {len(de_ids)}")

# Check indicators for issues
print(f"\n🔍 Indicator Validation:")

missing_program = []
missing_expression = []
orphaned_programs = []
invalid_expressions = []

for ind in indicators:
    shortname = ind.get('shortName', ind.get('id', 'UNKNOWN'))
    
    # Check program reference
    if not ind.get('program'):
        missing_program.append(shortname)
    else:
        prog_ref = ind.get('program', {})
        prog_id = prog_ref.get('id') if isinstance(prog_ref, dict) else prog_ref
        if prog_id and prog_id not in program_ids:
            orphaned_programs.append((shortname, prog_id))
    
    # Check expression
    if not ind.get('expression'):
        missing_expression.append(shortname)
    else:
        # Parse expression for data element references
        expr = ind.get('expression', '')
        # Look for #{...} patterns (data element references)
        matches = re.findall(r'#\{([a-zA-Z0-9]{11})\}', expr)
        for match in matches:
            if match not in de_ids:
                invalid_expressions.append((shortname, match))

# Report issues
issues_found = 0

if missing_program:
    print(f"\n❌ Missing Program ({len(missing_program)}):")
    for shortname in missing_program[:5]:
        print(f"   - {shortname}")
    issues_found += len(missing_program)

if orphaned_programs:
    print(f"\n❌ Orphaned Program References ({len(orphaned_programs)}):")
    for shortname, prog_id in orphaned_programs[:5]:
        print(f"   - {shortname}: {prog_id} (not found)")
    issues_found += len(orphaned_programs)

if missing_expression:
    print(f"\n❌ Missing Expression ({len(missing_expression)}):")
    for shortname in missing_expression[:5]:
        print(f"   - {shortname}")
    issues_found += len(missing_expression)

if invalid_expressions:
    print(f"\n❌ Invalid Expression References ({len(invalid_expressions)}):")
    for shortname, elem_id in invalid_expressions[:5]:
        print(f"   - {shortname}: {elem_id} (element not found)")
    issues_found += len(invalid_expressions)

if issues_found == 0:
    print(f"\n✅ No validation issues found in program indicators")

print(f"\n{'=' * 80}")
print(f"DIAGNOSIS: {'⚠️  ISSUES FOUND' if issues_found > 0 else '✅ METADATA OK'}")
print(f"           Total issues: {issues_found}")
print(f"{'=' * 80}")

# Provide remediation guidance
if issues_found > 0:
    print("\nREMEDIATION STEPS:")
    if orphaned_programs:
        print("1. Fix orphaned program references - verify program IDs are correct")
    if invalid_expressions:
        print("2. Fix invalid expression references - verify data element IDs in expressions")
    if missing_program or missing_expression:
        print("3. Add missing program and expression fields")
