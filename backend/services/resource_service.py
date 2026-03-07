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

    supabase.table("resources").update({
        "status": "available"
    }).eq("id", resource_id).execute()

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