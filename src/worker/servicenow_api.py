import requests, os
from dotenv import load_dotenv
load_dotenv()

BASE = os.getenv("SNOW_INSTANCE")
USER = os.getenv("SNOW_USER")
PASS = os.getenv("SNOW_PASS")

def create_incident(short_desc, description, severity):
    url = f"https://{BASE}.service-now.com/api/now/table/incident"

    urgency = None
    impact = None
    if severity == "CRITICAL":
        urgency = "1"
        impact = "1"
    elif severity == "HIGH":
        urgency = "2"
        impact = "1"
    elif severity == "MEDIUM":
        urgency = "2"
        impact = "2"
    elif severity == "LOW":
        urgency = "3"
        impact = "2"
    else:
        urgency = "3"
        impact = "3"



    payload = {
        "short_description": short_desc,
        "description": description,
        "urgency":urgency,
        "impact": impact
    }
    response = requests.post(url, json=payload, auth=(USER, PASS))
    
    if response.status_code == 201 or response.status_code == 200:
        return response.json()["result"]["number"]  
    else:
        print("ServiceNow Error:", response.text)
        return None
