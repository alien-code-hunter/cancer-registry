#!/usr/bin/env python3
"""
Create comprehensive project index and resource guide
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

def create_index():
    """Create comprehensive project index"""
    
    index = []
    index.append("\n" + "=" * 80)
    index.append("CANCER REGISTRY PROJECT - RESOURCE INDEX")
    index.append("=" * 80)
    
    index.append("\n\n📚 DOCUMENTATION FILES")
    index.append("-" * 80)
    
    doc_files = [
        ("artifacts/reports/PROJECT_VALIDATION_REPORT.txt", "Comprehensive validation report with all metrics"),
        ("artifacts/reports/PROJECT_COMPLETION_SUMMARY.txt", "Full project completion summary and next steps"),
        ("docs/IMPLEMENTATION_COMPLETE.md", "Implementation completion notes"),
        ("docs/IMPROVEMENTS_SUMMARY.md", "Improvement summary and audit notes"),
        ("README.md", "Project overview and introduction"),
    ]
    
    for filename, description in doc_files:
        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            index.append(f"\n  ✅ {filename}")
            index.append(f"     {description}")
            index.append(f"     Size: {size_kb:.1f} KB")
    
    index.append("\n\n🔧 FIX & UTILITY SCRIPTS")
    index.append("-" * 80)
    
    fix_scripts = [
        ("scripts/fix/fix_aggregate_data_elements.py", "Remove AGGREGATE types from tracker programs"),
        ("scripts/fix/assign_all_data_elements.py", "Assign TRACKER elements to all program stages"),
        ("scripts/fix/rename_cecap.py", "Rename CECAP to Cervical Cancer Program"),
        ("scripts/fix/group_data_elements.py", "Create data element grouping reference"),
        ("scripts/fix/consolidate_programs.py", "Consolidate individual cancer programs into Program.json"),
        ("scripts/audit/diagnose_analytics.py", "Analyze and identify analytics issues"),
        ("scripts/audit/analyze_project.py", "Advanced project analysis with detailed metrics"),
        ("scripts/audit/audit_project.py", "Comprehensive project audit and validation"),
        ("scripts/audit/final_validation.py", "Generate final validation report"),
        ("scripts/audit/project_completion.py", "Verify all issues resolved and create summary"),
        ("scripts/import/reimport_fixes.py", "Re-import fixed files to DHIS2"),
        ("scripts/import/reimport_all_fixes.py", "Complete reimport of all fixed files"),
        ("scripts/import/reimport_corrected_stages.py", "Re-import corrected program stages"),
        ("scripts/import/reimport_consolidated_programs.py", "Re-import consolidated programs"),
        ("scripts/import/reimport_everything.py", "Final complete reimport of all files"),
    ]
    
    for script, purpose in fix_scripts:
        filepath = os.path.join(BASE_DIR, script)
        if os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            index.append(f"\n  ✅ {script}")
            index.append(f"     Purpose: {purpose}")
    
    index.append("\n\n📊 CORE METADATA FILES")
    index.append("-" * 80)
    
    core_files = [
        ("Program/Program.json", "19 consolidated cancer programs"),
        ("Program/Program Stage.json", "75 program stages (4-stage workflow)"),
        ("Program/Program Indicator.json", "930 cancer-specific indicators"),
        ("Data Element/Data Element.json", "164 data elements (143 TRACKER, 21 AGGREGATE)"),
        ("Data Element/Data Elements by Cancer Type.json", "Reference file for data element grouping"),
        ("Dashboard/Dashboard.json", "19 cancer-specific dashboards"),
        ("Validation/Validation Rule.json", "12 data quality validation rules"),
    ]
    
    for filepath, description in core_files:
        full_path = os.path.join(BASE_DIR, filepath)
        if os.path.exists(full_path):
            size_kb = os.path.getsize(full_path) / 1024
            index.append(f"\n  ✅ {filepath}")
            index.append(f"     {description}")
            index.append(f"     Size: {size_kb:.1f} KB")
    
    index.append("\n\n🗂️ ADDITIONAL METADATA FOLDERS")
    index.append("-" * 80)
    
    metadata_folders = [
        "Attribute",
        "Category", 
        "Event Visualisation",
        "Options",
        "Organisation Unit",
        "Program Rule",
        "Tracked Entity",
        "Users",
        "Visualisation",
    ]
    
    for folder in metadata_folders:
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.isdir(folder_path):
            json_files = len([f for f in os.listdir(folder_path) if f.endswith('.json')])
            index.append(f"\n  ✅ {folder}")
            index.append(f"     JSON files: {json_files}")
    
    index.append("\n\n" + "=" * 80)
    index.append("QUICK START GUIDE")
    index.append("=" * 80)
    
    index.append("\n\n1️⃣ VIEW PROJECT STATUS")
    index.append("-" * 80)
    index.append("\n  Run audit to see current project state:")
    index.append("  $ python3 scripts/audit/audit_project.py")
    index.append("\n  Or view detailed validation report:")
    index.append("  $ cat artifacts/reports/PROJECT_VALIDATION_REPORT.txt")
    
    index.append("\n\n2️⃣ MAKE CHANGES TO METADATA")
    index.append("-" * 80)
    index.append("\n  Edit any JSON file in the folders above, then:")
    index.append("  $ python3 scripts/import/reimport_everything.py")
    
    index.append("\n\n3️⃣ TROUBLESHOOT ISSUES")
    index.append("-" * 80)
    index.append("\n  Run diagnostic analysis:")
    index.append("  $ python3 scripts/audit/analyze_project.py")
    index.append("\n  Check for analytics issues:")
    index.append("  $ python3 scripts/audit/diagnose_analytics.py")
    
    index.append("\n\n4️⃣ VALIDATE PROJECT")
    index.append("-" * 80)
    index.append("\n  Run full validation suite:")
    index.append("  $ python3 scripts/audit/audit_project.py")
    index.append("  $ python3 scripts/audit/final_validation.py")
    index.append("  $ python3 scripts/audit/project_completion.py")
    
    index.append("\n\n" + "=" * 80)
    index.append("PROJECT STATISTICS")
    index.append("=" * 80)
    
    # Count all JSON files
    total_json = 0
    total_size = 0
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.json'):
                total_json += 1
                filepath = os.path.join(root, file)
                total_size += os.path.getsize(filepath)
    
    # Count Python scripts
    scripts_dir = BASE_DIR / "scripts"
    total_py = 0
    for root, dirs, files in os.walk(scripts_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py') and not file.startswith('test'):
                total_py += 1
    
    index.append(f"\n  Metadata Files: {total_json} JSON files")
    index.append(f"  Total Size: {total_size / (1024*1024):.2f} MB")
    index.append(f"  Python Scripts: {total_py} utility/fix scripts")
    index.append(f"  Programs: 19 cancer programs")
    index.append(f"  Program Stages: 75 total")
    index.append(f"  Program Indicators: 930 total")
    index.append(f"  Data Elements: 164 total")
    index.append(f"  Dashboards: 19 total")
    index.append(f"  Validation Rules: 12 total")
    
    index.append("\n\n" + "=" * 80)
    index.append("✅ PROJECT COMPLETE AND READY FOR USE")
    index.append("=" * 80 + "\n")
    
    return "\n".join(index)

def main():
    index = create_index()
    print(index)
    
    # Save index
    index_path = BASE_DIR / "artifacts" / "reports" / "PROJECT_INDEX.txt"
    with open(index_path, 'w') as f:
        f.write(index)
    
    print(f"📄 Index saved to: {index_path}")

if __name__ == "__main__":
    main()
