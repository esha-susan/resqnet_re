# backend/app.py
# Flask application entry point.
# Registers all route blueprints and starts the server.

from flask import Flask
from flask_cors import CORS
from routes.health import health_bp
from routes.auth import auth_bp
from routes.incidents import incidents_bp
from routes.speech import speech_bp
from config import FLASK_PORT
from routes.resources import resources_bp

def create_app():
    app = Flask(__name__)
    
    # Allow larger uploads for audio files (max 25MB — Whisper's limit)
    app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
    
    # Allow React frontend (localhost:5173) to call this API
    CORS(app, origins=["http://localhost:5173"])

    # Register all route blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(speech_bp)
    app.register_blueprint(resources_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    print(f"🚨 ResQNet Backend running on port {FLASK_PORT}")
    app.run(debug=True, port=FLASK_PORT)