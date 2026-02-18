#!/bin/bash

# Cancer Registry Batch Import Script
# Imports remaining metadata files to DHIS2
# Uses CREATE_AND_UPDATE strategy to safely handle previously imported items

set -e

# Configuration
BASE_URL="http://localhost:8085"
USERNAME="Meduletu_Kamati"
PASSWORD='Covid19!#@$'
IMPORT_STRATEGY="CREATE_AND_UPDATE"  # Safely handles re-imports
ATOMIC_MODE="NONE"  # Continue on partial errors
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
SUCCESS=0
FAILED=0

# Log file
LOG_DIR="${BASE_DIR}/artifacts/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/import_$(date +%Y%m%d_%H%M%S).log"

echo "Starting batch import at $(date)" | tee "$LOG_FILE"
echo "Import Strategy: $IMPORT_STRATEGY" | tee -a "$LOG_FILE"
echo "Atomic Mode: $ATOMIC_MODE" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

# Function to import a single file
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
    
    # Make the API call and capture response
    RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -u "${USERNAME}:${PASSWORD}" \
        "${BASE_URL}/api/metadata?importStrategy=${IMPORT_STRATEGY}&atomicMode=${ATOMIC_MODE}" \
        -d @"$file" 2>&1)
    
    # Check if response contains OK status
    if echo "$RESPONSE" | grep -q '"status":"OK"'; then
        # Extract stats
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
        echo "Full response: $RESPONSE" >> "$LOG_FILE"
        ((FAILED++))
        return 1
    fi
}

# ============================================================================
# REMAINING IMPORTS - Data Sets and Validation Rules
# ============================================================================

echo -e "\n${YELLOW}=== Data Sets ===${NC}" | tee -a "$LOG_FILE"
import_file "${BASE_DIR}/Data Set/Data Set.json" "Data Sets"

echo -e "\n${YELLOW}=== Validation Rules ===${NC}" | tee -a "$LOG_FILE"
import_file "${BASE_DIR}/Validation/Validation Rule Group.json" "Validation Rule Groups"
import_file "${BASE_DIR}/Validation/Validation Rule.json" "Validation Rules"

# ============================================================================
# OPTIONAL: Re-import individual cancer programs (redundant but safe)
# ============================================================================

echo -e "\n${YELLOW}=== Individual Cancer Programs (Re-import) ===${NC}" | tee -a "$LOG_FILE"
for program_file in "${BASE_DIR}"/archive/programs/*Cancer\ Program.json; do
    if [ -f "$program_file" ]; then
        PROGRAM_NAME=$(basename "$program_file" .json)
        import_file "$program_file" "Cancer Program: $PROGRAM_NAME"
        sleep 1  # Brief pause between imports
    fi
done

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "\n---" | tee -a "$LOG_FILE"
echo "Import Summary:" | tee -a "$LOG_FILE"
echo "  Total files:    $TOTAL" | tee -a "$LOG_FILE"
echo -e "  ${GREEN}Successful: $SUCCESS${NC}" | tee -a "$LOG_FILE"
echo -e "  ${RED}Failed:     $FAILED${NC}" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "Completed at $(date)" | tee -a "$LOG_FILE"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All imports completed successfully!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some imports failed. Check $LOG_FILE for details.${NC}"
    exit 1
fi
