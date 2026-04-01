import os, sys
sys.path.append('c:\\Users\\SREESUTHA\\resqnet_re\\backend')
from services import supabase

users = supabase.auth.admin.list_users()
user = [u for u in users if u.email == 'sreekuttyandsreemon@gmail.com'][0]
meta = user.user_metadata
print("Meta:", meta)

resources = supabase.table('resources').select('*').execute().data
# Match resource_type and see if it yields incidents
r_type = meta.get('resource_type')
print("Resource Type:", r_type)

incidents = [r['current_incident_id'] for r in resources if r.get('type') == r_type and r.get('current_incident_id')]
print("Incidents matching type:", incidents)
