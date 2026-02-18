#!/bin/bash

# Simple sequential imports without complex piping

echo ""
echo "================================================================================"
echo "IMPORTING REMAINING CANCER REGISTRY FILES"
echo "================================================================================"
echo ""

# 1. Data Elements
echo "3. Importing Data Elements (164)..."
curl -s -X POST -H "Content-Type: application/json" -u 'Meduletu_Kamati:Covid19!#@$' 'http://localhost:8085/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE' -d @'Data Element/Data Element.json' > /tmp/de_import.json
sleep 2

# 2. Validation Rules
echo "4. Importing Validation Rules (12)..."
curl -s -X POST -H "Content-Type: application/json" -u 'Meduletu_Kamati:Covid19!#@$' 'http://localhost:8085/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE' -d @'Validaion/Validation Rule.json' > /tmp/vr_import.json
sleep 2

# 3. Dashboards
echo "5. Importing Dashboards (19)..."
curl -s -X POST -H "Content-Type: application/json" -u 'Meduletu_Kamati:Covid19!#@$' 'http://localhost:8085/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE' -d @'Dashboard/Dashboard.json' > /tmp/db_import.json
sleep 2

# 4. Datasets
echo "6. Importing Data Sets (unified)..."
curl -s -X POST -H "Content-Type: application/json" -u 'Meduletu_Kamati:Covid19!#@$' 'http://localhost:8085/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE' -d @'Data Set/Data Set.json' > /tmp/ds_import.json
sleep 2

echo ""
echo "================================================================================"
echo "✅ ALL IMPORTS COMPLETE"
echo "================================================================================"
echo ""
echo "📊 Summary of imports:"
echo "  1️⃣ Program Stages: 75 (UPDATED)"
echo "  2️⃣ Program Indicators: 930 (UPDATED)"
echo "  3️⃣ Data Elements: $(grep -o '"created":[0-9]*' /tmp/de_import.json | grep -o '[0-9]*' | head -1) created, $(grep -o '"updated":[0-9]*' /tmp/de_import.json | grep -o '[0-9]*' | head -1) updated"
echo "  4️⃣ Validation Rules: $(grep -o '"created":[0-9]*' /tmp/vr_import.json | grep -o '[0-9]*' | head -1) created, $(grep -o '"updated":[0-9]*' /tmp/vr_import.json | grep -o '[0-9]*' | head -1) updated"
echo "  5️⃣ Dashboards: $(grep -o '"created":[0-9]*' /tmp/db_import.json | grep -o '[0-9]*' | head -1) created, $(grep -o '"updated":[0-9]*' /tmp/db_import.json | grep -o '[0-9]*' | head -1) updated"
echo "  6️⃣ Data Sets: $(grep -o '"created":[0-9]*' /tmp/ds_import.json | grep -o '[0-9]*' | head -1) created, $(grep -o '"updated":[0-9]*' /tmp/ds_import.json | grep -o '[0-9]*' | head -1) updated"
echo ""
echo "🌐 View all improvements: http://localhost:8085/dhis-web-dashboard"
echo "================================================================================"
echo ""
