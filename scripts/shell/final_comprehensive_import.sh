#!/bin/bash

# Cancer Registry - Final Comprehensive Import
# Imports all improvements: program stages, indicators, validation rules, datasets

set -e

DHIS_URL="http://localhost:8085"
USERNAME="Meduletu_Kamati"
PASSWORD="Covid19!#@$"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "================================================================================"
echo "CANCER REGISTRY - FINAL COMPREHENSIVE IMPORT"
echo "================================================================================"
echo ""

# Function to import file
import_file() {
    local file=$1
    local description=$2
    
    echo "Importing: $description"
    echo "  File: $file"
    
    http_code=$(curl -s -o /tmp/import_response.json -w "%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -u "${USERNAME}:${PASSWORD}" \
        "${DHIS_URL}/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE" \
        -d @"${file}")
    
    if [ "$http_code" == "200" ]; then
        # Parse response
        summary=$(cat /tmp/import_response.json | python3 -c "import json, sys; d=json.load(sys.stdin); print('✓ ' + str(len(d.get('stats', {}).get('total', 0))) + ' items')" 2>/dev/null || echo "✓ Success")
        echo "  Status: $summary"
    else
        echo "  Status: FAILED (HTTP $http_code)"
        cat /tmp/import_response.json | python3 -m json.tool 2>/dev/null || cat /tmp/import_response.json
    fi
    echo ""
}

# Import Program Stages (with renamed stages)
import_file "${BASE_DIR}/Program/Program Stage.json" "Program Stages (75 stages - real-world clinical workflow)"

# Import Program Indicators (with proper program references)
import_file "${BASE_DIR}/Program/Program Indicator.json" "Program Indicators (1020 total - properly linked to programs)"

# Import Data Elements (enhanced)
import_file "${BASE_DIR}/Data Element/Data Element.json" "Data Elements (164 total - includes cancer-specific fields)"

# Import Dashboards (cancer-specific)
import_file "${BASE_DIR}/Dashboard/Dashboard.json" "Dashboards (19 total - CECAP + 18 cancer-specific)"

# Import Datasets
import_file "${BASE_DIR}/Data Set/Data Set.json" "Data Sets (unified for all cancers)"

# Import Validation Rules
import_file "${BASE_DIR}/Validation/Validation Rule.json" "Validation Rules (12 total - data quality assurance)"

# Import Visualizations
import_file "${BASE_DIR}/Visualisation/Visualisation.json" "Visualizations (59 total)"

# Import Event Visualizations
import_file "${BASE_DIR}/Event Visualisation/Even Visualisation.json" "Event Visualizations (33 total)"

# Import Program Rules
import_file "${BASE_DIR}/Program Rule/Program Rule.json" "Program Rules"

# Import Tracked Entities
import_file "${BASE_DIR}/Tracked Entity/Tracked Entity Type.json" "Tracked Entity Types"

# Import Organisation Units
import_file "${BASE_DIR}/Organisation Unit/Organisation Unit.json" "Organisation Units"

# Import Categories
import_file "${BASE_DIR}/Category/Category.json" "Categories"
import_file "${BASE_DIR}/Category/Category Option.json" "Category Options"
import_file "${BASE_DIR}/Category/Category Option Group.json" "Category Option Groups"

# Import attribute
import_file "${BASE_DIR}/Attribute/Attribute.json" "Attributes"

echo "================================================================================"
echo "✅ COMPREHENSIVE IMPORT COMPLETE"
echo "================================================================================"
echo ""
echo "Summary of improvements implemented:"
echo "  1️⃣  Program Stages: 75 stages renamed to real-world clinical workflow"
echo "  2️⃣  Program Indicators: 1020 indicators with proper program linkage"
echo "  3️⃣  Data Elements: 164 total (10 new cancer-specific fields)"
echo "  4️⃣  Validation Rules: 12 total (6 new data quality rules)"
echo "  5️⃣  Dashboards: 19 cancer-specific monitoring dashboards"
echo "  6️⃣  Datasets: Unified 'Cancer Registry Unified Dataset' for all cancers"
echo ""
echo "Real-world clinical workflow stages:"
echo "  - Stage 1: Initial Assessment & Diagnostics"
echo "  - Stage 2: Staging & Treatment Planning"
echo "  - Stage 3: Active Treatment"
echo "  - Stage 4: Follow-up & Outcomes"
echo ""
echo "Visit: http://localhost:8085 to view all improvements"
echo "================================================================================"
