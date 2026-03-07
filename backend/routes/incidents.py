from flask import Blueprint, jsonify, request
from middleware.auth_middleware import require_auth

from services.incident_service import (
    create_incident,
    get_all_incidents,
    update_incident_priority
)

from agents.priority_agent import analyze_incident

incidents_bp = Blueprint('incidents', __name__)


@incidents_bp.route('/api/incidents', methods=['POST'])
@require_auth
def create():

    body = request.get_json()

    required = ['title', 'description', 'location']
    missing = [f for f in required if not body.get(f)]

    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:

        priority_result = analyze_incident(
            body['title'],
            body['description']
        )

        final_priority = priority_result['priority']

        incident = create_incident(
            title=body['title'],
            description=body['description'],
            location=body['location'],
            priority=final_priority,
            user_id=request.current_user.id
        )

        incident['auto_priority'] = priority_result

        return jsonify(incident), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@incidents_bp.route('/api/incidents', methods=['GET'])
@require_auth
def get_all():

    incidents = get_all_incidents()

    return jsonify(incidents), 200


@incidents_bp.route('/api/incidents/<incident_id>/priority', methods=['PATCH'])
@require_auth
def update_priority(incident_id):

    body = request.get_json()
    priority = body.get('priority')

    if not priority:
        return jsonify({"error": "priority required"}), 400

    updated = update_incident_priority(incident_id, priority)

    return jsonify(updated), 200