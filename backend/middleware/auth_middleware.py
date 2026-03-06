from functools import wraps
from flask import request, jsonify
from services import supabase

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header.split(' ')[1]

        try:
            response = supabase.auth.get_user(token)

            if not response.user:
                return jsonify({"error": "Invalid token"}), 401

            request.current_user = response.user

        except Exception as e:
            return jsonify({"error": "Token verification failed", "details": str(e)}), 401

        return f(*args, **kwargs)

    return decorated