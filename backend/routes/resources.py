from flask import Blueprint, jsonify, request
from middleware.auth_middleware import require_auth
from services.resource_service import (
    get_all_resources,
    get_resources_by_status,
    release_resource,
    release_all_incident_resources,
    get_unreleased_resources,
    get_all_incident_resources
)
from agents.resource_agent import (
    allocate_resources,
    get_incident_resources
)

resources_bp = Blueprint('resources', __name__, url_prefix='/api/resources')


@resources_bp.route('', methods=['GET'])
@require_auth
def get_all():
    status = request.args.get('status')
    try:
        if status:
            data = get_resources_by_status(status)
        else:
            data = get_all_resources()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@resources_bp.route('/incident/<incident_id>', methods=['GET'])
@require_auth
def get_for_incident(incident_id):
    """Returns active (unreleased) resources for an incident."""
    try:
        data = get_unreleased_resources(incident_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@resources_bp.route('/incident/<incident_id>/all', methods=['GET'])
@require_auth
def get_all_for_incident(incident_id):
    """Returns ALL resources ever assigned to an incident."""
    try:
        data = get_all_incident_resources(incident_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@resources_bp.route('/allocate', methods=['POST'])
@require_auth
def allocate():
    body = request.get_json()
    incident_id = body.get('incident_id')
    resources = body.get('resources')  # e.g. [{ "type": "doctor", "count": 1 }]

    if not incident_id or not resources:
        return jsonify({"error": "Missing incident_id or resources"}), 400

    if not isinstance(resources, list) or len(resources) == 0:
        return jsonify({"error": "resources must be a non-empty array"}), 400

    try:
        result = allocate_resources(incident_id, resources)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@resources_bp.route('/release', methods=['POST'])
@require_auth
def release():
    """Release a single resource from an incident."""
    body = request.get_json()
    resource_id = body.get('resource_id')
    incident_id = body.get('incident_id')

    if not resource_id or not incident_id:
        return jsonify({"error": "Missing resource_id or incident_id"}), 400

    try:
        result = release_resource(resource_id, incident_id)
        return jsonify({"released": True, "data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@resources_bp.route('/release-all/<incident_id>', methods=['POST'])
@require_auth
def release_all(incident_id):
    """Release ALL resources from an incident."""
    try:
        count = release_all_incident_resources(incident_id)
        return jsonify({
            "released": True,
            "count": count,
            "message": f"{count} resources released"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500