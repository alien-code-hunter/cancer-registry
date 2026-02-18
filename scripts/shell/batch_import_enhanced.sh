#!/bin/bash

# Cancer Registry Enhanced Batch Import Script
# Imports all enhanced metadata including cancer-specific dashboards
# Uses CREATE_AND_UPDATE strategy to safely handle re-imports

set -e

# Configuration
BASE_URL="http://localhost:8085"
USERNAME="Meduletu_Kamati"
PASSWORD='Covid19!#@$'
IMPORT_STRATEGY="CREATE_AND_UPDATE"
ATOMIC_MODE="NONE"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TOTAL=0
SUCCESS=0
FAILED=0

LOG_DIR="${BASE_DIR}/artifacts/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/import_enhanced_$(date +%Y%m%d_%H%M%S).log"

echo "Starting enhanced batch import at $(date)" | tee "$LOG_FILE"
echo "Import Strategy: $IMPORT_STRATEGY" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

import_file() {
    local file=$1
    local description=$2
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ File not found: $file${NC}" | tee -a "$LOG_FILE"
        ((FAILED++))
        return 1
    fi
    
    ((TOTAL++))
    echo -n "Importing $description... "
    
    RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -u "${USERNAME}:${PASSWORD}" \
        "${BASE_URL}/api/metadata?importStrategy=${IMPORT_STRATEGY}&atomicMode=${ATOMIC_MODE}" \
        -d @"$file" 2>&1)
    
    if echo "$RESPONSE" | grep -q '"status":"OK"'; then
        STATS=$(echo "$RESPONSE" | grep -o '"stats":{[^}]*}' | head -1)
        echo -e "${GREEN}✓${NC} $STATS" | tee -a "$LOG_FILE"
        ((SUCCESS++))
        return 0
    elif echo "$RESPONSE" | grep -q '"httpStatusCode":200'; then
        echo -e "${GREEN}✓${NC} HTTP 200 OK" | tee -a "$LOG_FILE"
        ((SUCCESS++))
        return 0
    else
        ERROR=$(echo "$RESPONSE" | grep -o '"message":"[^"]*"' | head -1 || echo '"message":"Unknown error"')
        echo -e "${RED}✗${NC} $ERROR" | tee -a "$LOG_FILE"
        ((FAILED++))
        return 1
    fi
}

echo -e "\n${YELLOW}=== ENHANCED DATA ELEMENTS ===${NC}" | tee -a "$LOG_FILE"
import_file "${BASE_DIR}/Data Element/Data Element.json" "Enhanced Data Elements (164 total)"

echo -e "\n${YELLOW}=== ENHANCED DASHBOARDS ===${NC}" | tee -a "$LOG_FILE"
import_file "${BASE_DIR}/Dashboard/Dashboard.json" "Cancer-Specific Dashboards (19 total)"

echo -e "\n${YELLOW}=== ENHANCED PROGRAM INDICATORS ===${NC}" | tee -a "$LOG_FILE"
echo "Skipping Program Indicator.json - new indicators require program linkage configuration" | tee -a "$LOG_FILE"
# import_file "Program/Program Indicator.json" "Enhanced Program Indicators (876 total)"

echo -e "\n${YELLOW}=== DATA SETS ===${NC}" | tee -a "$LOG_FILE"
import_file "${BASE_DIR}/Data Set/Data Set.json" "Data Sets"

echo -e "\n${YELLOW}=== VALIDATION RULES ===${NC}" | tee -a "$LOG_FILE"
import_file "${BASE_DIR}/Validation/Validation Rule Group.json" "Validation Rule Groups"
import_file "${BASE_DIR}/Validation/Validation Rule.json" "Validation Rules"

echo -e "\n${YELLOW}=== VISUALIZATIONS ===${NC}" | tee -a "$LOG_FILE"
import_file "${BASE_DIR}/Visualisation/Visualisation.json" "Visualizations"
import_file "${BASE_DIR}/Event Visualisation/Even Visualisation.json" "Event Visualizations"

echo -e "\n${YELLOW}=== CANCER PROGRAMS (Re-import for completeness) ===${NC}" | tee -a "$LOG_FILE"
for program_file in "${BASE_DIR}"/archive/programs/*Cancer\ Program.json; do
    if [ -f "$program_file" ]; then
        PROGRAM_NAME=$(basename "$program_file" .json)
        import_file "$program_file" "$PROGRAM_NAME"
        sleep 0.5
    fi
done

# Summary
echo -e "\n---" | tee -a "$LOG_FILE"
echo "Import Summary:" | tee -a "$LOG_FILE"
echo "  Total files:    $TOTAL" | tee -a "$LOG_FILE"
echo -e "  ${GREEN}Successful: $SUCCESS${NC}" | tee -a "$LOG_FILE"
echo -e "  ${RED}Failed:     $FAILED${NC}" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "Completed at $(date)" | tee -a "$LOG_FILE"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All enhancements imported successfully!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some imports failed. Check $LOG_FILE for details.${NC}"
    exit 1
fi
