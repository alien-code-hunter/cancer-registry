Cancer Registry - DHIS2 Metadata
================================

Overview
--------
This repository contains DHIS2 metadata for a multi-cancer registry. It includes
19 cancer programs, standardized clinical workflow stages, program indicators,
dashboards, validation rules, and supporting metadata.

Highlights
----------
- 19 programs (18 cancer-specific + 1 cervical cancer program)
- 75 program stages (standard 4-stage workflow; cervical uses 3 stages)
- 930 program indicators
- 164 data elements (143 tracker, 21 aggregate)
- 19 dashboards
- 12 validation rules

Repository Structure
--------------------
- Attribute/, Category/, Options/, Organisation Unit/, Users/: supporting metadata
- Program/: consolidated programs, stages, indicators
- Dashboard/: dashboards
- Data Element/: data elements
- Data Set/: unified dataset
- Validation/: validation rules and groups
- Visualisation/, Event Visualisation/: visualizations
- scripts/: maintenance utilities
	- scripts/audit/: audits and validation reports
	- scripts/fix/: one-off fixes and cleanups
	- scripts/import/: import helpers
	- scripts/shell/: shell-based import scripts
- artifacts/: generated outputs
	- artifacts/reports/: validation and index reports
	- artifacts/logs/: import logs
	- artifacts/bundles/: bundle exports
- archive/programs/: archived individual cancer program files
- docs/: project documentation

Quick Start
-----------
1) Run a project audit:
	 python3 scripts/audit/audit_project.py

2) Generate a fresh index report:
	 python3 scripts/audit/create_project_index.py

3) Reimport metadata (choose one):
	 - Full import:
		 bash scripts/shell/import_all_improvements.sh
	 - Final batch import:
		 bash scripts/shell/import_final_files.sh

Notes
-----
- This repo is organized to keep generated outputs under artifacts/.
- Archived per-cancer program files are stored under archive/programs/ for reference.
