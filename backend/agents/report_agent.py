
from services import supabase
from datetime import datetime


def get_incident_details(incident_id: str) -> dict:
    """Fetches full incident data."""
    response = (
        supabase.table("incidents")
        .select("*")
        .eq("id", incident_id)
        .single()
        .execute()
    )
    return response.data


def get_all_assigned_resources(incident_id: str) -> list:
    """Fetches ALL resources ever assigned including released ones."""
    response = (
        supabase.table("incident_resources")
        .select("*, resources(*)")
        .eq("incident_id", incident_id)
        .execute()
    )
    return response.data or []


def get_call_logs(incident_id: str) -> list:
    """Fetches all call logs for the incident."""
    response = (
        supabase.table("call_logs")
        .select("*")
        .eq("incident_id", incident_id)
        .execute()
    )
    return response.data or []


def calculate_response_time(created_at: str, closed_at: str) -> str:
    """
    Calculates total response time between creation and closure.
    Returns human readable string like "1 hour 23 minutes".
    """
    try:
        # Parse timestamps
        fmt = "%Y-%m-%dT%H:%M:%S"
        start = datetime.fromisoformat(created_at.replace("Z", "").split(".")[0])
        end = datetime.fromisoformat(closed_at.replace("Z", "").split(".")[0])

        diff = end - start
        total_seconds = int(diff.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
        elif minutes > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''} {seconds} second{'s' if seconds != 1 else ''}"
        else:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
    except Exception:
        return "Unknown"


def generate_summary(incident: dict, resources: list, calls: list) -> str:
    """
    Auto-generates a plain English resolution summary
    based on the incident data.
    """
    priority = incident.get("priority", "Unknown")
    title = incident.get("title", "Unknown incident")
    location = incident.get("location", "Unknown location")

    total_resources = len(resources)
    resource_types = list(set([
        r["resources"]["type"].replace("_", " ")
        for r in resources if r.get("resources")
    ]))

    confirmed_calls = len([c for c in calls if c.get("status") == "confirmed"])
    total_calls = len(calls)

    summary = (
        f"A {priority} priority incident '{title}' was reported at {location}. "
        f"{total_resources} resource unit{'s' if total_resources != 1 else ''} "
        f"were deployed including {', '.join(resource_types) if resource_types else 'various units'}. "
    )

    if total_calls > 0:
        summary += (
            f"{confirmed_calls} out of {total_calls} "
            f"responder{'s' if total_calls != 1 else ''} confirmed availability. "
        )

    summary += "The incident has been successfully resolved and all resources have been released."

    return summary


def generate_report(incident_id: str) -> dict:
    """
    Main entry point for the Report Agent.
    Collects all data, builds report, saves to database.

    Returns the saved report dict.
    """
    # Step 1: Gather all data
    incident = get_incident_details(incident_id)
    if not incident:
        raise Exception(f"Incident {incident_id} not found")

    resources = get_all_assigned_resources(incident_id)
    calls = get_call_logs(incident_id)

    # Step 2: Calculate response time
    closed_at = incident.get("updated_at") or datetime.utcnow().isoformat()
    response_time = calculate_response_time(
        incident.get("created_at", ""),
        closed_at
    )

    # Step 3: Build resource summary
    resource_summary = {}
    for r in resources:
        rtype = r["resources"]["type"] if r.get("resources") else "unknown"
        resource_summary[rtype] = resource_summary.get(rtype, 0) + 1

    # Step 4: Build call summary
    call_summary = {
        "total": len(calls),
        "confirmed": len([c for c in calls if c.get("status") == "confirmed"]),
        "unavailable": len([c for c in calls if c.get("status") == "unavailable"]),
        "no_answer": len([c for c in calls if c.get("status") == "no_answer"]),
        "initiated": len([c for c in calls if c.get("status") == "initiated"]),
    }

    # Step 5: Generate resolution summary
    summary_text = generate_summary(incident, resources, calls)

    # Step 6: Build complete report
    report_data = {
        "incident": {
            "id": incident["id"],
            "title": incident["title"],
            "description": incident["description"],
            "location": incident["location"],
            "priority": incident["priority"],
            "status": incident["status"],
            "created_at": incident["created_at"],
            "closed_at": closed_at,
        },
        "timeline": {
            "reported": incident["created_at"],
            "closed": closed_at,
            "total_response_time": response_time,
        },
        "resources": {
            "total_deployed": len(resources),
            "breakdown": resource_summary,
            "details": [
                {
                    "type": r["resources"]["type"] if r.get("resources") else "unknown",
                    "location": r["resources"]["location"] if r.get("resources") else "unknown",
                    "assigned_at": r.get("assigned_at"),
                    "released_at": r.get("released_at"),
                }
                for r in resources
            ]
        },
        "calls": {
            "summary": call_summary,
            "logs": [
                {
                    "responder": c.get("responder_name"),
                    "phone": c.get("phone"),
                    "status": c.get("status"),
                    "time": c.get("created_at"),
                }
                for c in calls
            ]
        },
        "resolution_summary": summary_text,
        "generated_at": datetime.utcnow().isoformat(),
    }

    # Step 7: Save report to database
    response = supabase.table("reports").insert({
        "incident_id": incident_id,
        "report_data": report_data
    }).execute()

    if not response.data:
        raise Exception("Failed to save report to database")

    return response.data[0]
