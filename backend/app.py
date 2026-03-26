from flask import Flask, request
from flask_cors import CORS

from routes.health import health_bp
from routes.auth import auth_bp
from routes.incidents import incidents_bp
from routes.speech import speech_bp
from routes.resources import resources_bp
from routes.twilio_webhook import twilio_bp
from routes.reports import reports_bp
from routes.dashboard import dashboard_bp

from config import FLASK_PORT


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

    # ✅ CORS (correct + complete)
    CORS(
        app,
        origins=["http://localhost:5173"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    # ✅ GLOBAL FIX for preflight (VERY IMPORTANT)
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            return '', 200

    # ✅ Register routes
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(speech_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(twilio_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(dashboard_bp)

    print("\n🚀 REGISTERED ROUTES:")
    for rule in app.url_map.iter_rules():
        print(rule)

    return app


if __name__ == '__main__':
    app = create_app()
    print(f"🚨 Backend running on port {FLASK_PORT}")
    app.run(debug=True, port=FLASK_PORT)