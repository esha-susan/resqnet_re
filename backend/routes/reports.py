from flask import Blueprint, jsonify
from middleware.auth_middleware import require_auth
from services import supabase

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@reports_bp.route('', methods=['GET'])
@require_auth
def get_all_reports():
    """Returns all generated reports newest first."""
    try:
        response = (
            supabase.table("reports")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route('/<incident_id>', methods=['GET'])
@require_auth
def get_report(incident_id):
    """Returns the report for a specific incident."""
    try:
        response = (
            supabase.table("reports")
            .select("*")
            .eq("incident_id", incident_id)
            .single()
            .execute()
        )
        if not response.data:
            return jsonify({"error": "Report not found"}), 404
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
