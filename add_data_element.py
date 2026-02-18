#!/usr/bin/env python3
import json
import subprocess
import sys

def run_curl(method, url, data=None):
    """Run curl command and return parsed JSON response."""
    cmd = ['curl', '-s', '-X', method, '-H', 'Content-Type: application/json',
           '-u', 'Meduletu_Kamati:Covid19!#@$', url]
    
    if data:
        cmd.extend(['-d', json.dumps(data)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return {"error": result.stdout[:200]}

# Get current stage
print("Fetching stage ymx76J82mIm...")
stage_data = run_curl('GET', 'http://localhost:8085/api/programStages/ymx76J82mIm')

if 'error' in stage_data:
    print(f"Error fetching stage: {stage_data['error']}")
    sys.exit(1)

elements = stage_data.get('programStageDataElements', [])
elem_ids = [e.get('dataElement', {}).get('id') for e in elements]

if 'AswNlG485pW' in elem_ids:
    print("✓ Element AswNlG485pW already exists in stage")
else:
    print(f"Current elements: {len(elem_ids)}")
    print("Adding AswNlG485pW...")
    
    # Add the new element
    new_element = {
        "dataElement": {"id": "AswNlG485pW"},
        "compulsory": False,
        "allowProvidedElsewhere": False,
        "allowFutureDate": False,
        "sortOrder": 65
    }
    stage_data['programStageDataElements'].append(new_element)
    
    # PUT back to DHIS2
    put_response = run_curl('PUT', 'http://localhost:8085/api/programStages/ymx76J82mIm', stage_data)
    print(f"Update response: {json.dumps(put_response)[:150]}")
    
    # Verify
    print("Verifying...")
    verify_data = run_curl('GET', 'http://localhost:8085/api/programStages/ymx76J82mIm?fields=programStageDataElements')
    verify_elements = [e.get('dataElement', {}).get('id') for e in 
                      verify_data.get('programStageDataElements', [])]
    
    if 'AswNlG485pW' in verify_elements:
        print(f"✓ Data element successfully added! Stage now has {len(verify_elements)} elements")
    else:
        print("✗ Data element NOT found after update")
        sys.exit(1)
