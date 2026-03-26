# backend/routes/reports.py
from flask import Blueprint, jsonify, request, send_file
from io import BytesIO
from middleware.auth_middleware import require_auth
from services import supabase
from services.report_service import aggregate_report_data, generate_pdf_report

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


def _get_user_role(user) -> tuple[str, str]:
    """Returns (role, full_name) for the current user."""
    profile_res = (
        supabase.table("profiles")
        .select("role, full_name")
        .eq("id", user.id)
        .single()
        .execute()
    )
    profile   = profile_res.data or {}
    role      = profile.get("role", "responder")
    full_name = profile.get("full_name") or user.email or "Unknown"
    return role, full_name


@reports_bp.route('', methods=['GET'])
@require_auth
def get_all_reports():
    """Returns all generated incident reports newest first."""
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


@reports_bp.route('/generate', methods=['POST'])
@require_auth
def generate_report():
    """
    Generates a role-scoped PDF analytics report.

    Request body:
        { "range": "weekly" | "monthly" }

    Admin  → sees all incidents platform-wide.
    Others → sees only incidents linked to their resource type.
    """
    body      = request.get_json() or {}
    range_str = body.get('range', 'weekly')

    if range_str not in ('weekly', 'monthly'):
        return jsonify({"error": "range must be 'weekly' or 'monthly'"}), 400

    try:
        role, full_name = _get_user_role(request.current_user)
        data            = aggregate_report_data(request.current_user.id, role, range_str)
        pdf_bytes       = generate_pdf_report(data, full_name)

        filename = f"resqnet_{role}_{range_str}_report.pdf"

        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500