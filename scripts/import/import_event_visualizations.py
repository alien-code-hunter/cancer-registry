#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
import base64

BASE_URL = "http://localhost:8085"
USERNAME = "Meduletu_Kamati"
PASSWORD = "Covid19!#@$"

# Create auth header
credentials = f"{USERNAME}:{PASSWORD}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
auth_header = f"Basic {encoded_credentials}"

print("=" * 80)
print("IMPORTING EVENT VISUALISATIONS")
print("=" * 80)

# Import event visualisations
with open('Event Visualisation/Even Visualisation.json', 'r') as f:
    event_viz_data = json.load(f)

json_bytes = json.dumps(event_viz_data).encode('utf-8')
req = urllib.request.Request(
    f"{BASE_URL}/api/metadata?importStrategy=CREATE_AND_UPDATE&atomicMode=NONE",
    data=json_bytes,
    headers={
        'Content-Type': 'application/json',
        'Authorization': auth_header
    },
    method='POST'
)

try:
    response = urllib.request.urlopen(req, timeout=60)
    result = json.loads(response.read().decode('utf-8'))
    
    if result.get('status') == 'OK':
        print(f"✅ Event visualisations imported successfully")
    else:
        print(f"⚠️ Import status: {result.get('status')}")
        if 'typeReports' in result:
            for report in result['typeReports']:
                print(f"   - {report}")
except urllib.error.HTTPError as e:
    error_response = e.read().decode('utf-8')
    print(f"❌ HTTP Error {e.code}")
    print(error_response[:500])
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n✅ All visualizations are now imported.")
