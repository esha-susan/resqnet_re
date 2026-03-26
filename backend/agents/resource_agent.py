# backend/agents/resource_agent.py
from services import supabase
from datetime import datetime

RESOURCE_RULES = {
    "Critical": {
        "ambulance":  2,
        "fire_truck": 2,
        "doctor":     2,
        "police":     2
    },
    "High": {
        "ambulance":  2,
        "fire_truck": 1,
        "doctor":     1
    },
    "Medium": {
        "ambulance": 1,
        "doctor":    1
    },
    "Low": {
        "police": 1
    }
}

def get_available_resources(resource_type: str, quantity: int) -> list:
    response = (
        supabase.table("resources")
        .select("*")
        .eq("type", resource_type)
        .eq("status", "available")
        .limit(quantity)
        .execute()
    )
    return response.data or []

def assign_resource(resource_id: str, incident_id: str) -> dict:
    supabase.table("resources").update({
        "status": "busy"
    }).eq("id", resource_id).execute()

    response = supabase.table("incident_resources").insert({
        "incident_id": incident_id,
        "resource_id": resource_id,
        "assigned_at": datetime.utcnow().isoformat()
    }).execute()

    return response.data[0] if response.data else {}

def allocate_resources(incident_id: str, priority: str,
                       incident_title: str = "Incident",
                       incident_location: str = "Unknown",
                       incident_description: str = "") -> dict:
    """
    Allocates resources based on priority rules and triggers Twilio calls.
    """
    requirements = RESOURCE_RULES.get(priority, RESOURCE_RULES["Low"])
    assigned = []
    unavailable = []

    for resource_type, quantity_needed in requirements.items():
        available = get_available_resources(resource_type, quantity_needed)
        if not available:
            unavailable.append(resource_type)
            continue

        for resource in available:
            assign_resource(resource["id"], incident_id)
            assigned.append({
                "id":       resource["id"],
                "type":     resource["type"],
                "location": resource.get("location", "Unknown")
            })

    # Update incident status to in_progress
    if assigned:
        supabase.table("incidents").update({
            "status": "in_progress",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", incident_id).execute()

    # Trigger Twilio calls
    call_results = []
    try:
        from agents.twilio_agent import call_all_responders
        call_results = call_all_responders(
            incident_id=incident_id,
            assigned_resources=assigned,
            incident_title=incident_title,
            incident_location=incident_location,
            priority=priority,
            incident_description=incident_description
        )
    except Exception as e:
        print(f"⚠️ Twilio calling failed: {e}")

    return {
        "assigned":       assigned,
        "unavailable":    unavailable,
        "total_assigned": len(assigned),
        "calls":          call_results
    }

def get_incident_resources(incident_id: str) -> list:
    response = (
        supabase.table("incident_resources")
        .select("*, resources(*)")
        .eq("incident_id", incident_id)
        .is_("released_at", "null")
        .execute()
    )
    return response.data or []