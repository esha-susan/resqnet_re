import traceback
import sys
sys.path.append('c:\\Users\\SREESUTHA\\resqnet_re\\backend')
from services import supabase

try:
    incidents_res = supabase.table("incidents").select("*").execute()
    resources_res = supabase.table("resources").select("*").execute()
    calls_res = supabase.table("call_logs").select("*").execute()
    # Let's fix reports_res since it was select('id') inside the route
    reports_res = supabase.table("reports").select("id").execute()

    incidents = incidents_res.data or []
    resources = resources_res.data or []
    calls = calls_res.data or []
    reports = reports_res.data or []

    # Simulate role='admin'
    role = 'admin'
    phone = None

    if role == 'responder' and phone:
        assigned_incident_ids = set([c["incident_id"] for c in calls if c["phone"] == phone])
        incidents = [i for i in incidents if i["id"] in assigned_incident_ids]
        calls = [c for c in calls if c["incident_id"] in assigned_incident_ids]
        reports = [r for r in reports if r.get("incident_id") in assigned_incident_ids]

    incident_stats = {
        "total": len(incidents),
        "open": len([i for i in incidents if i["status"] == "open"]),
        "in_progress": len([i for i in incidents if i["status"] == "in_progress"]),
        "closed": len([i for i in incidents if i["status"] == "closed"]),
    }

    priority_stats = {
        "critical": len([i for i in incidents if i["priority"] == "Critical"]),
        "high": len([i for i in incidents if i["priority"] == "High"]),
        "medium": len([i for i in incidents if i["priority"] == "Medium"]),
        "low": len([i for i in incidents if i["priority"] == "Low"]),
    }

    resource_stats = {
        "total": len(resources),
        "available": len([r for r in resources if r["status"] == "available"]),
        "busy": len([r for r in resources if r["status"] == "busy"]),
    }

    resource_types = {}
    for r in resources:
        rtype = r["type"]
        if rtype not in resource_types:
            resource_types[rtype] = {"available": 0, "busy": 0}
        resource_types[rtype][r["status"]] += 1

    call_stats = {
        "total": len(calls),
        "confirmed": len([c for c in calls if c["status"] == "confirmed"]),
        "unavailable": len([c for c in calls if c["status"] == "unavailable"]),
        "no_answer": len([c for c in calls if c["status"] == "no_answer"]),
    }

    active = [i for i in incidents if i["status"] != "closed"]
    active_sorted = sorted(
        active,
        key=lambda x: x["created_at"],
        reverse=True
    )[:5]

    closed = [i for i in incidents if i["status"] == "closed"]
    closed_sorted = sorted(
        closed,
        key=lambda x: x["created_at"],
        reverse=True
    )[:3]

    print("Success! Data built correctly.")
    print("Total Incidents calculated as:", incident_stats["total"])

except Exception as e:
    print("FAILED WITH EXCEPTION!")
    traceback.print_exc()
