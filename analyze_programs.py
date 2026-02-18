#!/usr/bin/env python3
"""
Identify orphaned program references and fix them
"""
import json

print("=" * 80)
print("PROGRAM REFERENCE ANALYSIS")
print("=" * 80)

# Load programs
with open('Program/Program.json') as f:
    prog_data = json.load(f)

programs = prog_data.get('programs', [])
program_ids = {p.get('id'): p.get('name') for p in programs}

print(f"\n✅ Programs in Program.json ({len(programs)}):")
for prog_id, prog_name in program_ids.items():
    print(f"   {prog_id}: {prog_name}")

# Load indicators
with open('Program/Program Indicator.json') as f:
    pi_data = json.load(f)

indicators = pi_data.get('programIndicators', [])

# Get unique program references from indicators
prog_refs = {}
for ind in indicators:
    prog_ref = ind.get('program', {})
    prog_id = prog_ref.get('id') if isinstance(prog_ref, dict) else prog_ref
    if prog_id:
        if prog_id not in prog_refs:
            prog_refs[prog_id] = []
        prog_refs[prog_id].append(ind.get('shortName', ind.get('id')))

print(f"\n📊 Programs Referenced in Indicators ({len(prog_refs)}):")
for prog_id, ind_names in prog_refs.items():
    exists = "✅" if prog_id in program_ids else "❌"
    name = program_ids.get(prog_id, "NOT FOUND")
    print(f"   {exists} {prog_id} ({name}): {len(ind_names)} indicators")

# Find orphaned references
orphaned = {pid: inds for pid, inds in prog_refs.items() if pid not in program_ids}
print(f"\n❌ Orphaned Program References: {len(orphaned)}")

if orphaned:
    print("\n   Orphaned program IDs:")
    for prog_id, ind_names in orphaned.items():
        print(f"   - {prog_id}: {len(ind_names)} indicators reference this")
        print(f"     Sample indicators: {', '.join(ind_names[:3])}")
