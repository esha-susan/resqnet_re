# backend/services/incident_service.py
from services import supabase
from datetime import datetime

VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Critical']
VALID_STATUSES = ['open', 'in_progress', 'closed']


def create_incident(title, description, location, priority, user_id):
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority. Must be one of: {VALID_PRIORITIES}")

    data = {
        "title": title,
        "description": description,
        "location": location,
        "priority": priority,
        "status": "open",
        "created_by": user_id
    }

    response = supabase.table("incidents").insert(data).execute()

    if not response.data:
        raise Exception("Failed to create incident in database")

    return response.data[0]


def get_all_incidents():
    response = (
        supabase.table("incidents")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


def get_incident_by_id(incident_id):
    response = (
        supabase.table("incidents")
        .select("*")
        .eq("id", incident_id)
        .single()
        .execute()
    )
    return response.data


def update_incident_status(incident_id, status):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status. Must be one of: {VALID_STATUSES}")

    response = (
        supabase.table("incidents")
        .update({
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        })
        .eq("id", incident_id)
        .execute()
    )

    if not response.data:
        raise Exception("Incident not found or update failed")

    return response.data[0]


def update_incident_priority(incident_id, priority):
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority. Must be one of: {VALID_PRIORITIES}")

    response = (
        supabase.table("incidents")
        .update({
            "priority": priority,
            "updated_at": datetime.utcnow().isoformat()
        })
        .eq("id", incident_id)
        .execute()
    )

    if not response.data:
        raise Exception("Incident not found or update failed")

    return response.data[0]