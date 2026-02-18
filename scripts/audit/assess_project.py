#!/usr/bin/env python3
import json
import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parents[2]

# ============================================================================
# COMPREHENSIVE PROJECT ASSESSMENT
# ============================================================================

print("=" * 70)
print("CANCER REGISTRY PROJECT ASSESSMENT")
print("=" * 70)

# 1. CHECK CANCER PROGRAMS
print("\n1. CANCER PROGRAMS")
print("-" * 70)
cancer_programs = {}
program_dir = BASE_DIR / "archive" / "programs"

for program_file in sorted(program_dir.glob("*Cancer Program.json")):
    with open(program_file) as f:
        data = json.load(f)
    if data.get('programs'):
        prog = data['programs'][0]
        prog_id = prog.get('id')
        cancer_programs[prog_id] = {
            'name': prog.get('displayName', prog.get('name')),
            'stages': len(prog.get('programStages', [])),
            'indicators': len(prog.get('programIndicators', [])),
            'tracked_entity_type': prog.get('trackedEntityType', {}).get('id')
        }

print(f"Total cancer programs: {len(cancer_programs)}")
for prog_id, info in cancer_programs.items():
    print(f"  ✓ {info['name']}")
    print(f"    - Stages: {info['stages']}, Indicators: {info['indicators']}")

# 2. CHECK DATA ELEMENTS
print("\n2. DATA ELEMENTS")
print("-" * 70)
de_file = BASE_DIR / "Data Element" / "Data Element.json"
de_data = json.load(open(de_file))
data_elements = de_data.get('dataElements', [])
print(f"Total data elements: {len(data_elements)}")

# Check for standard cancer data elements
standard_de = ['Age', 'Gender', 'Diagnosis', 'Stage', 'Treatment', 'Outcome']
found_de = set()
for de in data_elements:
    name = de.get('name', '').lower()
    for std in standard_de:
        if std.lower() in name:
            found_de.add(std)

print(f"Essential data elements found: {len(found_de)}/{len(standard_de)}")
for std in standard_de:
    status = "✓" if std in found_de else "✗"
    print(f"  {status} {std}")

# 3. CHECK PROGRAM INDICATORS
print("\n3. PROGRAM INDICATORS")
print("-" * 70)
pi_file = BASE_DIR / "Program" / "Program Indicator.json"
pi_data = json.load(open(pi_file))
program_indicators = pi_data.get('programIndicators', [])
print(f"Total program indicators: {len(program_indicators)}")

# 4. CHECK VISUALIZATIONS
print("\n4. VISUALIZATIONS & DASHBOARDS")
print("-" * 70)
viz_file = BASE_DIR / "Visualisation" / "Visualisation.json"
viz_data = json.load(open(viz_file))
visualizations = viz_data.get('visualizations', [])
print(f"Total visualizations: {len(visualizations)}")

# Check event visualizations
ev_file = BASE_DIR / "Event Visualisation" / "Even Visualisation.json"
if ev_file.exists():
    ev_data = json.load(open(ev_file))
    event_viz = ev_data.get('eventVisualizations', [])
    print(f"Total event visualizations: {len(event_viz)}")

# Check dashboards
dash_file = BASE_DIR / "Dashboard" / "Dashboard.json"
dash_data = json.load(open(dash_file))
dashboards = dash_data.get('dashboards', [])
print(f"Total dashboards: {len(dashboards)}")
for dash in dashboards:
    print(f"  - {dash.get('name')}")

# 5. DATA CAPTURE PROCESS CHECK
print("\n5. DATA CAPTURE PROCESS")
print("-" * 70)
ps_file = BASE_DIR / "Program" / "Program Stage.json"
ps_data = json.load(open(ps_file))
program_stages = ps_data.get('programStages', [])
print(f"Total program stages: {len(program_stages)}")

# Check stage data elements
stages_with_elements = sum(1 for ps in program_stages if ps.get('programStageDataElements'))
print(f"Stages with data elements: {stages_with_elements}/{len(program_stages)}")

# 6. PROGRAM RULES
print("\n6. PROGRAM RULES")
print("-" * 70)
pr_file = BASE_DIR / "Program Rule" / "Program Rule.json"
pr_data = json.load(open(pr_file))
program_rules = pr_data.get('programRules', [])
print(f"Total program rules: {len(program_rules)}")

# Count by rule type
rule_types = defaultdict(int)
for rule in program_rules:
    rule_type = "Unknown"
    if "hide" in rule.get('name', '').lower():
        rule_type = "HIDE"
    elif "show" in rule.get('name', '').lower():
        rule_type = "SHOW"
    elif "mandatory" in rule.get('name', '').lower():
        rule_type = "MANDATORY"
    elif "assign" in rule.get('name', '').lower():
        rule_type = "ASSIGN"
    rule_types[rule_type] += 1

for rule_type, count in sorted(rule_types.items()):
    print(f"  {rule_type}: {count}")

# 7. MISSING ITEMS
print("\n7. COMPLETENESS CHECK")
print("-" * 70)
missing = []

if len(dashboards) < len(cancer_programs):
    missing.append(f"Missing dashboards for {len(cancer_programs) - len(dashboards)} cancer types")

if len(visualizations) < 5:
    missing.append(f"Limited visualizations ({len(visualizations)} found)")

if len(event_viz) == 0:
    missing.append("No event visualizations created")

if not found_de:
    missing.append("Basic data elements may be missing")

if missing:
    print("Issues found:")
    for issue in missing:
        print(f"  ✗ {issue}")
else:
    print("✓ Project appears complete")

print("\n" + "=" * 70)
print("ASSESSMENT COMPLETE")
print("=" * 70)
