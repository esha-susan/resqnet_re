# backend/app.py
from flask import Flask
from flask_cors import CORS
from routes.health import health_bp
from routes.auth import auth_bp
from routes.incidents import incidents_bp
from routes.speech import speech_bp
from routes.resources import resources_bp
from routes.twilio_webhook import twilio_bp     # ← NEW
from config import FLASK_PORT

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
    CORS(app, origins=["http://localhost:5173"])

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(speech_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(twilio_bp)           # ← NEW

    return app

if __name__ == '__main__':
    app = create_app()
    print(f"🚨 ResQNet Backend running on port {FLASK_PORT}")
    app.run(debug=True, port=FLASK_PORT)