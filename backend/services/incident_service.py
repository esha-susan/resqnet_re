from services import supabase
from datetime import datetime

VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Critical']


def create_incident(title, description, location, priority, user_id):

    if priority not in VALID_PRIORITIES:
        raise ValueError("Invalid priority")

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
        raise Exception("Failed to create incident")

    return response.data[0]


def get_all_incidents():
    response = (
        supabase.table("incidents")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data


def update_incident_priority(incident_id, priority):

    response = (
        supabase.table("incidents")
        .update({
            "priority": priority,
            "updated_at": datetime.utcnow().isoformat()
        })
        .eq("id", incident_id)
        .execute()
    )

    return response.data[0]