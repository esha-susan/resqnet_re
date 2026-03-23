# backend/routes/incidents.py
import threading
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
from services.resource_service import (
    release_all_incident_resources,
    get_unreleased_resources
)
from agents.report_agent import generate_report

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

        # Step 3: Allocate resources + trigger Twilio calls
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


@incidents_bp.route('/api/incidents/<incident_id>/close', methods=['POST'])
@require_auth
def close_incident(incident_id):
    """
    Closes incident:
    1. Releases all resources immediately
    2. Sets status to closed immediately
    3. Generates report in background after 15s delay
       (gives Twilio time to process keypress and update call_logs)
    """
    try:
        incident = get_incident_by_id(incident_id)
        if not incident:
            return jsonify({"error": "Incident not found"}), 404

        if incident['status'] == 'closed':
            return jsonify({"error": "Incident is already closed"}), 400

        # Step 1: Release all resources
        released_count = release_all_incident_resources(incident_id)

        # Step 2: Close the incident
        closed = update_incident_status(incident_id, 'closed')

        # Step 3: Generate report in background after delay
        def delayed_report(inc_id):
            import time
            time.sleep(15)
            try:
                generate_report(inc_id)
                print(f"✅ Report generated for incident {inc_id}")
            except Exception as e:
                print(f"⚠️ Report generation failed: {e}")

        thread = threading.Thread(
            target=delayed_report,
            args=(incident_id,)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            "incident": closed,
            "resources_released": released_count,
            "report_generated": True,
            "report_id": None,
            "message": f"Incident closed. {released_count} resources released. Report generating in background."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500