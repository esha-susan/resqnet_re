# backend/routes/incidents.py
import threading
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import require_auth
from services.auth_service import get_user_profile
from services.incident_service import (
    create_incident,
    get_all_incidents,
    get_incidents_for_role,
    get_incident_by_id,
    update_incident_status,
    update_incident_priority
)
from agents.priority_agent import analyze_incident
from agents.resource_agent import allocate_resources, get_available_resources, assign_resource
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
        profile = get_user_profile(request.current_user)
        role = profile.get("role")
        
        if role == "admin":
            return jsonify(get_all_incidents()), 200
        else:
            return jsonify(get_incidents_for_role(role)), 200
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


# ── THIS IS NOW CORRECTLY OUTSIDE close_incident ──────────────────────────────
@incidents_bp.route('/api/incidents/<incident_id>/add-resources', methods=['POST'])
@require_auth
def add_extra_resources(incident_id):
    """
    Manually add extra resources to an existing open/in-progress incident.
    Triggers Twilio dispatch calls for ONLY the newly assigned resources.

    Request body:
        {
            "resources": [
                { "type": "fire_truck", "count": 2 },
                { "type": "ambulance", "count": 1 }
            ]
        }
    """
    try:
        # ── 1. Validate incident ──────────────────────────────────────────────
        incident = get_incident_by_id(incident_id)
        if not incident:
            return jsonify({"error": "Incident not found"}), 404
        if incident['status'] == 'closed':
            return jsonify({"error": "Cannot add resources to a closed incident"}), 400

        body = request.get_json()
        resource_requests = body.get('resources', [])

        if not resource_requests:
            return jsonify({"error": "No resources specified"}), 400

        # ── 2. Assign the requested resources ────────────────────────────────
        assigned    = []
        unavailable = []

        for req in resource_requests:
            resource_type = req.get('type', '').strip()
            count         = int(req.get('count', 1))

            if not resource_type or count < 1:
                continue

            available = get_available_resources(resource_type, count)

            if not available:
                unavailable.append({
                    "type":      resource_type,
                    "requested": count,
                    "reason":    "No available resources of this type"
                })
                continue

            for resource in available:
                assign_resource(resource["id"], incident_id)
                assigned.append({
                    "id":       resource["id"],
                    "type":     resource["type"],
                    "location": resource.get("location", "Unknown")
                })

            # Partial fulfillment — note the shortfall
            if len(available) < count:
                unavailable.append({
                    "type":      resource_type,
                    "requested": count,
                    "fulfilled": len(available),
                    "reason":    f"Only {len(available)} of {count} available"
                })

        # ── 3. Twilio dispatch for newly assigned resources only ──────────────
        call_results = []
        if assigned:
            try:
                from agents.twilio_agent import call_all_responders
                call_results = call_all_responders(
                    incident_id=incident_id,
                    assigned_resources=assigned,
                    incident_title=incident['title'],
                    incident_location=incident['location'],
                    priority=incident['priority'],
                    incident_description=incident.get('description', '')
                )
            except Exception as e:
                print(f"⚠️ Twilio calling failed for extra resources: {e}")

        return jsonify({
            "incident_id":    incident_id,
            "assigned":       assigned,
            "unavailable":    unavailable,
            "total_assigned": len(assigned),
            "calls":          call_results,
            "message": (
                f"{len(assigned)} resource(s) added and dispatched."
                if assigned else
                "No resources could be assigned — none available."
            )
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500