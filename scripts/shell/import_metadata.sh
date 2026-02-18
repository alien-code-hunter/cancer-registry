#!/bin/bash

# Comprehensive metadata import for Cancer Registry
# Imports all necessary metadata in correct dependency order

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DHIS2_URL="http://localhost:8085"
DHIS2_USER="Meduletu_Kamati:Covid19!#@$"

echo ""
echo "================================================================================"
echo "CANCER REGISTRY METADATA IMPORT"
echo "================================================================================"
echo ""
echo "🔄 Importing metadata to DHIS2..."
echo ""

# Function to import and report
import_metadata() {
    local file=$1
    local label=$2
    local count=$3
    
    echo "📦 Importing ${label} (${count})..."
    
    response=$(curl -s -X POST -H "Content-Type: application/json" \
        -u "${DHIS2_USER}" \
        "${DHIS2_URL}/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE" \
        -d @"${BASE_DIR}/${file}")
    
    # Extract stats
    created=$(echo "$response" | grep -o '"created":[0-9]*' | head -1 | grep -o '[0-9]*')
    updated=$(echo "$response" | grep -o '"updated":[0-9]*' | head -1 | grep -o '[0-9]*')
    ignored=$(echo "$response" | grep -o '"ignored":[0-9]*' | head -1 | grep -o '[0-9]*')
    
    # Check for errors
    if echo "$response" | grep -q '"status":"ERROR"'; then
        echo "   ❌ Failed - check response below:"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        return 1
    else
        echo "   ✅ Created: ${created:-0}, Updated: ${updated:-0}, Ignored: ${ignored:-0}"
        return 0
    fi
    
    sleep 2
}

# 1. Attributes
import_metadata "Attribute/Attribute.json" "Attributes" "~50"

# 2. Categories (required by data elements)
import_metadata "Category/Category.json" "Categories" "~20"
import_metadata "Category/Category Option.json" "Category Options" "~50"
import_metadata "Category/Category Combo.json" "Category Combos" "~15"
import_metadata "Category/Category Option Combo.json" "Category Option Combos" "~30"

# 3. Option Sets (required by data elements)
import_metadata "Options/Option.json" "Options" "~200"
import_metadata "Options/Option Set.json" "Option Sets" "~50"
import_metadata "Options/Option group.json" "Option Groups" "~30"

# 4. Organisation Units
import_metadata "Organisation Unit/Organisation Unit.json" "Organisation Units" "~30"
import_metadata "Organisation Unit/Organisation unit Group.json" "Organisation Unit Groups" "~10"
import_metadata "Organisation Unit/Organisation Unit Level.json" "Organisation Unit Levels" "~5"

# 5. Users and Roles
import_metadata "Users/User Role.json" "User Roles" "~10"
import_metadata "Users/User group.json" "User Groups" "~10"

# 6. Tracked Entity Types and Attributes
import_metadata "Tracked Entity/Tracked Entity Type.json" "Tracked Entity Types" "~5"
import_metadata "Tracked Entity/Tracked Entity Attribute.json" "Tracked Entity Attributes" "~30"

# 7. Data Elements (both tracker and aggregate - 542 total)
import_metadata "Data Element/Data Element.json" "Data Elements" "542"
import_metadata "Data Element/Data Element Group.json" "Data Element Groups" "~40"
import_metadata "Data Element/Data Element Group Set.json" "Data Element Group Sets" "~5"

# 8. Indicators (aggregate indicators - 38 total)
import_metadata "Options/Indicator Type.json" "Indicator Types" "~5"
import_metadata "Options/Indicator.json" "Indicators" "38"
import_metadata "Options/indicator group.json" "Indicator Groups" "~20"
import_metadata "Options/Indicator Group Set.json" "Indicator Group Sets" "~3"

# 9. Programs (19 cancer programs)
import_metadata "Program/Program.json" "Programs" "19"

# 10. Program Stages (75 stages - CECAP has 143 elements, others have 45 generic elements)
import_metadata "Program/Program Stage.json" "Program Stages" "75"

# 11. Program Indicators (930 indicators)
import_metadata "Program/Program Indicator.json" "Program Indicators" "930"

# 12. Program Rules
import_metadata "Program Rule/Program Rule.json" "Program Rules" "~100"
import_metadata "Program Rule/Program Rule Variable.json" "Program Rule Variables" "~150"
import_metadata "Program Rule/Program Rule Action.json" "Program Rule Actions" "~100"

# 13. Validation Rules
import_metadata "Validation/Validation Rule.json" "Validation Rules" "~12"
import_metadata "Validation/Validation Rule Group.json" "Validation Rule Groups" "~5"

# 14. Data Sets
import_metadata "Data Set/Data Set.json" "Data Sets" "~20"

# 15. Visualizations
import_metadata "Visualisation/Visualisation.json" "Visualizations" "~50"
import_metadata "Event Visualisation/Even Visualisation.json" "Event Visualizations" "~20"

# 16. Dashboards
import_metadata "Dashboard/Dashboard.json" "Dashboards" "~19"

echo ""
echo "================================================================================"
echo "✅ METADATA IMPORT COMPLETE"
echo "================================================================================"
echo ""
echo "📊 Summary:"
echo "  • 19 Cancer Programs (1 CECAP + 18 others)"
echo "  • 75 Program Stages (CECAP: 143 elements/stage, Others: 45 generic elements/stage)"
echo "  • 542 Data Elements (143 tracker + 399 aggregate)"
echo "  • 38 Aggregate Indicators" 
echo "  • 930 Program Indicators"
echo "  • 36 Element/Indicator Groups (18 Data Element + 18 Indicator Groups)"
echo ""
echo "🔍 Key Features:"
echo "  ✓ Cervical cancer elements (73) only in CECAP program"
echo "  ✓ Generic cancer elements (70) in all 19 programs"
echo "  ✓ Aggregate elements cloned for 18 non-cervical cancers"
echo "  ✓ Cancer-specific groupings for reporting"
echo ""
echo "🌐 Access DHIS2: ${DHIS2_URL}"
echo "================================================================================"
echo ""
