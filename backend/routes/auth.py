from flask import Blueprint, jsonify, request
from middleware.auth_middleware import require_auth
from services.auth_service import get_user_profile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/profile', methods=['GET'])
@require_auth
def profile():
    """
    Returns the logged-in user's profile.
    The middleware already verified the token and
    attached the user to request.current_user.
    """
    user_profile = get_user_profile(request.current_user)
    return jsonify(user_profile), 200