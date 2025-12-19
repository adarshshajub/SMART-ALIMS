import requests, os
from dotenv import load_dotenv
load_dotenv()

BASE = os.getenv("SNOW_INSTANCE")
USER = os.getenv("SNOW_USER")
PASS = os.getenv("SNOW_PASS")

def create_incident(short_desc, description):
    url = f"{BASE}/api/now/table/incident"
    payload = {
        "short_description": short_desc,
        "description": description,
        "urgency": "2",
        "impact": "2"
    }
    response = requests.post(url, json=payload, auth=(USER, PASS))
    
    if response.status_code == 201 or response.status_code == 200:
        return response.json()["result"]["number"]  # e.g., INC0012345
    else:
        print("ServiceNow Error:", response.text)
        return None
