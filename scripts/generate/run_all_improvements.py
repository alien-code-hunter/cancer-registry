#!/usr/bin/env python3
"""Run all 4 major cancer registry improvements"""

import subprocess
import sys
from pathlib import Path

scripts_to_run = [
    ("1. Improve Program Stages", "scripts/legacy/improve_program_stages.py"),
    ("2-4. Improve Datasets, Indicators & Validation", "scripts/legacy/improve_datasets_indicators_validation.py")
]

BASE_DIR = Path(__file__).resolve().parents[2]

print("=" * 80)
print("RUNNING CANCER REGISTRY COMPREHENSIVE IMPROVEMENTS")
print("=" * 80)

for title, script in scripts_to_run:
    print(f"\nRunning: {title}")
    print("-" * 80)
    result = subprocess.run(
        [sys.executable, script],
        cwd=str(BASE_DIR)
    )
    if result.returncode != 0:
        print(f"❌ Error running {script}")
        sys.exit(1)

print("\n" + "=" * 80)
print("✅ ALL IMPROVEMENTS COMPLETED SUCCESSFULLY")
print("=" * 80)
