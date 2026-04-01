import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import supabase
from agents.resource_agent import allocate_additional_resources
from datetime import datetime
import json

def test_add_more():
    print("Testing add_more_resources functionality...")
    
    # 1. Fetch an existing incident that is in_progress, or create one
    incidents = supabase.table("incidents").select("*").limit(1).execute()
    if not incidents.data:
        print("No incidents found in DB. Please ensure there is at least one incident.")
        return
        
    incident = incidents.data[0]
    incident_id = incident["id"]
    print(f"Using incident_id: {incident_id}")
    
    # 2. Add some more resources
    additional = {
        "police": 1
    }
    print(f"Adding additional resources: {additional}")
    
    try:
        result = allocate_additional_resources(incident_id, additional)
        print("Result:")
        print(json.dumps(result, indent=2))
        
        # 3. Verify in DB
        res = supabase.table("incident_resources").select("*").eq("incident_id", incident_id).execute()
        print("\nAll assigned resources for this incident:")
        for r in res.data:
            print(f"- Resource ID: {r['resource_id']}, Type: {r.get('assignment_type', 'initial')}")
            
    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(f"Exception details:\n")
            import traceback
            traceback.print_exc(file=f)
            f.write(f"\nError during allocation: {e}")
        print("Error encountered, written to error_log.txt")

if __name__ == "__main__":
    test_add_more()
