from flask import Blueprint, jsonify
from middleware.auth_middleware import require_auth
from services import supabase

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """
    Returns complete dashboard stats in a single API call:
    - Incident counts by status
    - Incident counts by priority
    - Resource counts by status
    - Resource counts by type
    - Recent incidents (last 5)
    - Call stats
    - Report count
    """
    try:
        # ── Fetch all data in parallel ──
        incidents_res  = supabase.table("incidents").select("*").execute()
        resources_res  = supabase.table("resources").select("*").execute()
        calls_res      = supabase.table("call_logs").select("*").execute()
        reports_res    = supabase.table("reports").select("id").execute()

        incidents = incidents_res.data or []
        resources = resources_res.data or []
        calls     = calls_res.data or []
        reports   = reports_res.data or []

        # ── Incident Stats ──
        incident_stats = {
            "total":       len(incidents),
            "open":        len([i for i in incidents if i["status"] == "open"]),
            "in_progress": len([i for i in incidents if i["status"] == "in_progress"]),
            "closed":      len([i for i in incidents if i["status"] == "closed"]),
        }

        # ── Incident by Priority ──
        priority_stats = {
            "critical": len([i for i in incidents if i["priority"] == "Critical"]),
            "high":     len([i for i in incidents if i["priority"] == "High"]),
            "medium":   len([i for i in incidents if i["priority"] == "Medium"]),
            "low":      len([i for i in incidents if i["priority"] == "Low"]),
        }

        # ── Resource Stats ──
        resource_stats = {
            "total":     len(resources),
            "available": len([r for r in resources if r["status"] == "available"]),
            "busy":      len([r for r in resources if r["status"] == "busy"]),
        }

        # ── Resource by Type ──
        resource_types = {}
        for r in resources:
            rtype = r["type"]
            if rtype not in resource_types:
                resource_types[rtype] = {"available": 0, "busy": 0}
            resource_types[rtype][r["status"]] += 1

        # ── Call Stats ──
        call_stats = {
            "total":       len(calls),
            "confirmed":   len([c for c in calls if c["status"] == "confirmed"]),
            "unavailable": len([c for c in calls if c["status"] == "unavailable"]),
            "no_answer":   len([c for c in calls if c["status"] == "no_answer"]),
        }

        # ── Recent Incidents (last 5 active) ──
        active = [i for i in incidents if i["status"] != "closed"]
        active_sorted = sorted(
            active,
            key=lambda x: x["created_at"],
            reverse=True
        )[:5]

        # ── Recent Closed (last 3) ──
        closed = [i for i in incidents if i["status"] == "closed"]
        closed_sorted = sorted(
            closed,
            key=lambda x: x["created_at"],
            reverse=True
        )[:3]

        return jsonify({
            "incidents":      incident_stats,
            "priorities":     priority_stats,
            "resources":      resource_stats,
            "resource_types": resource_types,
            "calls":          call_stats,
            "reports_count":  len(reports),
            "active_incidents":  active_sorted,
            "closed_incidents":  closed_sorted,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
