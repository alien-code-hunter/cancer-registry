#!/bin/bash

# Import Cancer Element and Indicator Groups to DHIS2

DHIS2_URL="http://localhost:8085"
USERNAME="Meduletu_Kamati"
PASSWORD="Covid19!#@\$"

echo "📤 Importing Data Element Groups..."
curl -s -X POST \
  -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  "$DHIS2_URL/api/dataElementGroups" \
  -d "$(python3 -c "
import json
with open('Data Element/Data Element Group.json') as f:
    data = json.load(f)
print(json.dumps({'dataElementGroups': data['dataElementGroups']}))" )" | python3 -m json.tool | head -30

echo ""
echo "📤 Importing Indicator Groups..."
curl -s -X POST \
  -u "$USERNAME:$PASSWORD" \
  -H "Content-Type: application/json" \
  "$DHIS2_URL/api/indicatorGroups" \
  -d "$(python3 -c "
import json
with open('Options/Indicator Group.json') as f:
    data = json.load(f)
print(json.dumps({'indicatorGroups': data['indicatorGroups']}))" )" | python3 -m json.tool | head -30

echo ""
echo "✅ Import complete!"
