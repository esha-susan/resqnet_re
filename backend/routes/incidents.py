# backend/routes/incidents.py
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import require_auth
from services.incident_service import (
    create_incident,
    get_all_incidents,
    get_incident_by_id,
    update_incident_status,
    update_incident_priority
)
from agents.priority_agent import analyze_incident
from agents.resource_agent import allocate_resources

incidents_bp = Blueprint('incidents', __name__)


@incidents_bp.route('/api/incidents', methods=['POST'])
@require_auth
def create():
    body = request.get_json()

    required = ['title', 'description', 'location']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        # Step 1: Auto-assign priority
        priority_result = analyze_incident(
            title=body['title'],
            description=body['description']
        )
        final_priority = priority_result['priority']

        # Step 2: Create incident
        incident = create_incident(
            title=body['title'],
            description=body['description'],
            location=body['location'],
            priority=final_priority,
            user_id=request.current_user.id
        )

        # Step 3: Allocate resources + trigger calls with full details
        resource_result = allocate_resources(
            incident_id=incident['id'],
            priority=final_priority,
            incident_title=body['title'],
            incident_location=body['location'],
            incident_description=body['description']
        )

        incident['auto_priority'] = priority_result
        incident['resources'] = resource_result

        return jsonify(incident), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@incidents_bp.route('/api/incidents', methods=['GET'])
@require_auth
def get_all():
    try:
        return jsonify(get_all_incidents()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@incidents_bp.route('/api/incidents/<incident_id>', methods=['GET'])
@require_auth
def get_one(incident_id):
    try:
        incident = get_incident_by_id(incident_id)
        if not incident:
            return jsonify({"error": "Incident not found"}), 404
        return jsonify(incident), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@incidents_bp.route('/api/incidents/<incident_id>/status', methods=['PATCH'])
@require_auth
def update_status(incident_id):
    body = request.get_json()
    status = body.get('status')
    if not status:
        return jsonify({"error": "Missing field: status"}), 400
    try:
        updated = update_incident_status(incident_id, status)
        return jsonify(updated), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@incidents_bp.route('/api/incidents/<incident_id>/priority', methods=['PATCH'])
@require_auth
def update_priority(incident_id):
    body = request.get_json()
    priority = body.get('priority')
    if not priority:
        return jsonify({"error": "Missing field: priority"}), 400
    try:
        updated = update_incident_priority(incident_id, priority)
        return jsonify(updated), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500