import os, sys, requests
sys.path.append('c:\\Users\\SREESUTHA\\resqnet_re\\backend')
from services import supabase

# Login to get token
res = supabase.auth.sign_in_with_password({
    "email": "potterheadsree@gmail.com",
    "password": "password123" # assuming standard test password, if not I will just use service key to mint a token or check direct function
})

token = res.session.access_token

headers = {"Authorization": f"Bearer {token}"}
resp = requests.get("http://127.0.0.1:5000/api/dashboard/stats", headers=headers)
print("Status:", resp.status_code)
print("Response JSON:")
print(resp.json())
