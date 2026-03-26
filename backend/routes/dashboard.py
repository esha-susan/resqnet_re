from flask import Blueprint, jsonify, request
from middleware.auth_middleware import require_auth
from services import supabase
from services.auth_service import get_user_profile

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


def get_responder_incident_ids(user_id: str) -> list:
    res = (
        supabase.table("resources")
        .select("id")
        .eq("user_id", user_id)
        .execute()
    )

    resource_ids = [r["id"] for r in (res.data or [])]

    if not resource_ids:
        return []

    ir = (
        supabase.table("incident_resources")
        .select("incident_id")
        .in_("resource_id", resource_ids)
        .execute()
    )

    return list({row["incident_id"] for row in (ir.data or [])})


@dashboard_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    try:
        profile = get_user_profile(request.current_user)
        role = profile["role"]
        is_admin = role == "admin"
        user_id = profile["id"]

        # ───── Fetch base data ─────
        resources = supabase.table("resources").select("*").execute().data or []
        calls = supabase.table("call_logs").select("*").execute().data or []
        reports = supabase.table("reports").select("id").execute().data or []

        # ───── Incidents ─────
        if is_admin:
            incidents = supabase.table("incidents").select("*").execute().data or []
        else:
            incident_ids = get_responder_incident_ids(user_id)

            incidents = (
                supabase.table("incidents")
                .select("*")
                .in_("id", incident_ids)
                .execute()
                .data or []
            ) if incident_ids else []

        # ───── Incident Stats ─────
        incident_stats = {
            "total": len(incidents),
            "open": len([i for i in incidents if i["status"] == "open"]),
            "in_progress": len([i for i in incidents if i["status"] == "in_progress"]),
            "closed": len([i for i in incidents if i["status"] == "closed"]),
        }

        # ───── Priority Stats ─────
        priority_stats = {
            "critical": len([i for i in incidents if (i.get("priority") or "").lower() == "critical"]),
            "high": len([i for i in incidents if (i.get("priority") or "").lower() == "high"]),
            "medium": len([i for i in incidents if (i.get("priority") or "").lower() == "medium"]),
            "low": len([i for i in incidents if (i.get("priority") or "").lower() == "low"]),
        }

        # ───── Resource Stats (ONLY USER'S) ─────
        if is_admin:
            filtered_resources = resources
        else:
            filtered_resources = [
                r for r in resources if r.get("user_id") == user_id
            ]

        resource_stats = {
            "total": len(filtered_resources),
            "available": len([r for r in filtered_resources if r["status"] == "available"]),
            "busy": len([r for r in filtered_resources if r["status"] == "busy"]),
        }

        # 🔥🔥🔥 THIS IS THE MISSING PART (YOUR FIX)
        resource_types = {}

        for r in filtered_resources:
            r_type = r.get("type", "unknown")

            if r_type not in resource_types:
                resource_types[r_type] = {
                    "available": 0,
                    "busy": 0
                }

            if r["status"] == "available":
                resource_types[r_type]["available"] += 1
            else:
                resource_types[r_type]["busy"] += 1

        # ───── Call Stats ─────
        call_stats = {
            "total": len(calls),
            "confirmed": len([c for c in calls if c["status"] == "confirmed"]),
            "no_answer": len([c for c in calls if c["status"] == "no_answer"]),
        }

        # ───── Recent Incidents ─────
        active = sorted(
            [i for i in incidents if i["status"] != "closed"],
            key=lambda x: x["created_at"],
            reverse=True
        )[:5]

        closed = sorted(
            [i for i in incidents if i["status"] == "closed"],
            key=lambda x: x["created_at"],
            reverse=True
        )[:3]

        return jsonify({
            "role": role,
            "incidents": incident_stats,
            "priorities": priority_stats,
            "resources": resource_stats,

            # ✅ ADD THIS LINE
            "resource_types": resource_types,

            "calls": call_stats,
            "reports_count": len(reports) if is_admin else 0,
            "active_incidents": active,
            "closed_incidents": closed,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500