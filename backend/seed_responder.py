import os, sys
sys.path.append('c:\\Users\\SREESUTHA\\resqnet_re\\backend')
from services import supabase

phone = "+918078433433"

# 1. Create a fake incident
incident_data = {
    "title": "Industrial Factory Fire",
    "description": "Large scale fire at abandoned warehouse. Multiple units needed.",
    "location": "Warehouse District, Sector 4",
    "priority": "Critical",
    "status": "in_progress",
    "latitude": 34.0522,
    "longitude": -118.2437
}

inc_res = supabase.table("incidents").insert(incident_data).execute()
incident_id = inc_res.data[0]["id"]
print("Created Incident:", incident_id)

# 2. Create a call log linking the phone to the incident
call_data = {
    "incident_id": incident_id,
    "phone": phone,
    "responder_name": "Sreekutty",
    "status": "confirmed",
    "call_sid": "CA1234567890abcdef1234567890abcdef"
}

call_res = supabase.table("call_logs").insert(call_data).execute()
print("Created Call Log mapping to phone:", call_res.data[0]["phone"])

# 3. Create a fake resource assigned
resource_data = {
    "name": "Unit 42 - Police Squad",
    "type": "police",
    "status": "busy",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "current_incident_id": incident_id
}
res_res = supabase.table("resources").insert(resource_data).execute()
print("Assigned Resource:", res_res.data[0]["name"])

print("SUCCESS: Seeded dashboard data. The user will now see this incident on their dashboard.")
