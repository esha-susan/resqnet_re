import os
import sys
from dotenv import load_dotenv

# Try to load .env from backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table("incidents").select("id, title, status").execute()
for r in res.data:
    print(f"Title: {r['title']}, Status: {r['status']}")
