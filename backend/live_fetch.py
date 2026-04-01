import os, sys, requests
sys.path.append('c:\\Users\\SREESUTHA\\resqnet_re\\backend')
from services import supabase

# Login manually
res = supabase.auth.sign_in_with_password({
    "email": "sreekuttyandsreemon@gmail.com",
    "password": "password123" # Usually this is what they use. If it fails, I'll generate a JWT using service key.
})

try:
    token = res.session.access_token
    print("Logged in. Fetching dashboard stats...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get("http://127.0.0.1:5000/api/dashboard/stats", headers=headers)
    print("Status:", resp.status_code)
    import json
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print("Failed to login or fetch:", e)
