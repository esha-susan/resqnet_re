# backend/routes/resources.py
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import require_auth
from services.resource_service import (
    get_all_resources,
    get_resources_by_status,
    release_resource,
    release_all_incident_resources
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
    try:
        data = get_incident_resources(incident_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@resources_bp.route('/allocate', methods=['POST'])
@require_auth
def allocate():
    body = request.get_json()
    incident_id = body.get('incident_id')
    priority = body.get('priority')

    if not incident_id or not priority:
        return jsonify({"error": "Missing incident_id or priority"}), 400

    try:
        result = allocate_resources(incident_id, priority)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@resources_bp.route('/release', methods=['POST'])
@require_auth
def release():
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
    try:
        count = release_all_incident_resources(incident_id)
        return jsonify({
            "released": True,
            "count": count,
            "message": f"{count} resources released"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500