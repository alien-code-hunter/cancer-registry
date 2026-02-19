#!/bin/bash
# DHIS2 Bulk Metadata Import Script
# Usage: bash import_all_metadata.sh

DHIS2_URL="http://localhost:8085/api/metadata"
DHIS2_USER="Meduletu_Kamati"
DHIS2_PASS="Covid19!#@$"

# Import order: Category, Option, Organisation Unit, Tracked Entity, Data Element, Indicator, Program, Data Set, Dashboard, Event Visualisation, Visualisation, Users, Validation


import_file() {
  file="$1"
  # Skip if file is empty or not a regular file
  if [ ! -s "$file" ] || [ ! -f "$file" ]; then
    echo "Skipping empty or invalid file: $file"
    return
  fi
  echo "Importing $file ..."
  curl -s -u "$DHIS2_USER:$DHIS2_PASS" -X POST -H "Content-Type: application/json" \
    -d @"$file" "$DHIS2_URL" | grep -E 'status|importCount|error|ERROR' || echo "Imported $file"
}

# 1. Category
for f in Category/*.json; do import_file "$f"; done
# 2. Options
for f in Options/*.json; do import_file "$f"; done
# 3. Organisation Unit
for f in Organisation\ Unit/*.json; do import_file "$f"; done
# 4. Tracked Entity
for f in Tracked\ Entity/*.json; do import_file "$f"; done
# 5. Data Element
for f in Data\ Element/*.json; do import_file "$f"; done
# 6. Indicator
for f in Indicator/*.json; do import_file "$f"; done
# 7. Program
for f in Program/*.json; do import_file "$f"; done
# 8. Program Rule
for f in Program\ Rule/*.json; do import_file "$f"; done
# 9. Data Set
for f in Data\ Set/*.json; do import_file "$f"; done
# 10. Dashboard
for f in Dashboard/*.json; do import_file "$f"; done
# 11. Event Visualisation
for f in Event\ Visualisation/*.json; do import_file "$f"; done
# 12. Visualisation
for f in Visualisation/*.json; do import_file "$f"; done
# 13. Users
for f in Users/*.json; do import_file "$f"; done
# 14. Validation
for f in Validation/*.json; do import_file "$f"; done

echo "All metadata files imported. Check DHIS2 for results."
