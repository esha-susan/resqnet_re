import os, sys, json
sys.path.append('c:\\Users\\SREESUTHA\\resqnet_re\\backend')
from services import supabase

# Let's see if there is any user in auth to inspect
users_res = supabase.auth.admin.list_users()
users = users_res  # sometimes list_users returns list directly
for user in users:
    if user.email == "potterheadsree@gmail.com":
        print(f"User: {user.email}")
        print(f"Has attr user_metadata: {hasattr(user, 'user_metadata')}")
        print(f"user_metadata: {getattr(user, 'user_metadata', None)}")
