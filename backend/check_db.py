import os, sys
sys.path.append('c:\\Users\\SREESUTHA\\resqnet_re\\backend')
from services import supabase

res = supabase.table('incidents').select('*').execute()
print(f"Total incidents: {len(res.data)}")
for i in res.data:
    print(i['title'])
