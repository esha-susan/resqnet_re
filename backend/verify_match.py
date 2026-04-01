import os, sys
sys.path.append('c:\\Users\\SREESUTHA\\resqnet_re\\backend')
from services import supabase

calls = supabase.table('call_logs').select('*').execute().data
incidents = supabase.table('incidents').select('*').execute().data

# Test logic for specific phone
phone = "+918078433433"
assigned_incident_ids = set([c['incident_id'] for c in calls if c.get('phone') == phone])
incidents_res = [i for i in incidents if i['id'] in assigned_incident_ids]

print("Total Call Logs in DB:", len(calls))
print("Call Logs for this phone:", len([c for c in calls if c.get('phone') == phone]))
print("Assigned Incident IDs:", assigned_incident_ids)
print("Incidents matching those IDs in DB:", len(incidents_res))
if len(incidents_res) > 0:
    print("Match found:", incidents_res[0]["title"])
else:
    print("NO MATCH! The incident ID in call_logs does NOT exist in the incidents table!")
