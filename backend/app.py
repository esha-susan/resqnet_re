from flask import Flask
from flask_cors import CORS
from routes.health import health_bp
from routes.auth import auth_bp
from config import FLASK_PORT

def create_app():
    app = Flask(__name__)
    
    # Allow React frontend (localhost:5173) to call this API
    CORS(app, origins=["http://localhost:5173"])
    
    # Register route blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)   # NEW
    
    return app

if __name__ == '__main__':
    app = create_app()
    print(f"🚨 ResQNet Backend running on port {FLASK_PORT}")
    app.run(debug=True, port=FLASK_PORT)