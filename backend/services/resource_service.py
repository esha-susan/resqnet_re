from services import supabase
from datetime import datetime

def get_all_resources() -> list:
    response = (
        supabase.table("resources")
        .select("*")
        .order("type")
        .execute()
    )
    return response.data or []


def get_resources_by_status(status: str) -> list:
    response = (
        supabase.table("resources")
        .select("*")
        .eq("status", status)
        .execute()
    )
    return response.data or []


def release_resource(resource_id: str, incident_id: str) -> dict:
    """
    Releases a single resource back to available.
    Sets released_at timestamp in incident_resources.
    """
    # Mark resource as available
    supabase.table("resources").update({
        "status": "available"
    }).eq("id", resource_id).execute()

    # Record release time
    response = (
        supabase.table("incident_resources")
        .update({
            "released_at": datetime.utcnow().isoformat()
        })
        .eq("resource_id", resource_id)
        .eq("incident_id", incident_id)
        .is_("released_at", "null")
        .execute()
    )
    return response.data[0] if response.data else {}


def release_all_incident_resources(incident_id: str) -> int:
    """
    Releases ALL resources from an incident at once.
    Called when closing an incident.
    Returns count of released resources.
    """
    # Get all active assignments
    assignments = (
        supabase.table("incident_resources")
        .select("resource_id")
        .eq("incident_id", incident_id)
        .is_("released_at", "null")
        .execute()
    )

    if not assignments.data:
        return 0

    count = 0
    for assignment in assignments.data:
        release_resource(assignment["resource_id"], incident_id)
        count += 1

    return count


def get_unreleased_resources(incident_id: str) -> list:
    """
    Returns resources still active (not yet released) for an incident.
    Used to check if incident can be closed.
    """
    response = (
        supabase.table("incident_resources")
        .select("*, resources(*)")
        .eq("incident_id", incident_id)
        .is_("released_at", "null")
        .execute()
    )
    return response.data or []


def get_all_incident_resources(incident_id: str) -> list:
    """
    Returns ALL resources ever assigned to an incident
    including already released ones.
    """
    response = (
        supabase.table("incident_resources")
        .select("*, resources(*)")
        .eq("incident_id", incident_id)
        .execute()
    )
    return response.data or []