# backend/routes/speech.py
# HTTP endpoints for the Speech Agent.
# Handles audio file uploads and returns transcripts.

import os
import uuid
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from middleware.auth_middleware import require_auth
from agents.speech_agent import process_audio

# url_prefix means all routes here automatically start with /api/speech
speech_bp = Blueprint('speech', __name__, url_prefix='/api/speech')

# Temp folder to store uploaded audio before processing
TEMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp_audio')

# Allowed audio formats Whisper supports
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'wav', 'webm', 'm4a', 'ogg', 'flac'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_temp_dir():
    """Create temp_audio folder if it doesn't exist."""
    os.makedirs(TEMP_DIR, exist_ok=True)


@speech_bp.route('/transcribe', methods=['POST'])
@require_auth
def transcribe():
    """
    Accepts an audio file upload, runs Whisper, returns transcript.
    
    Form data:
        - audio: the audio file (required)
        - incident_id: UUID to link transcript to incident (optional)
    
    If incident_id provided → transcript saved to DB
    If not → transcript returned only (for preview before incident creation)
    """
    ensure_temp_dir()
    
    # Validate file exists in request
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    incident_id = request.form.get('incident_id')  # optional
    
    if audio_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    if not allowed_file(audio_file.filename):
        return jsonify({
            "error": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    # Save file temporarily with a unique name to avoid conflicts
    ext = audio_file.filename.rsplit('.', 1)[1].lower()
    temp_filename = f"{uuid.uuid4()}.{ext}"
    temp_path = os.path.join(TEMP_DIR, temp_filename)
    
    try:
        # Save uploaded file to disk
        audio_file.save(temp_path)
        
        # Run the Speech Agent
        result = process_audio(temp_path, incident_id)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
    
    finally:
        # Always delete temp file after processing — don't store audio
        if os.path.exists(temp_path):
            os.remove(temp_path)


@speech_bp.route('/transcripts/<incident_id>', methods=['GET'])
@require_auth
def get_transcripts(incident_id):
    """
    Returns all transcripts linked to a specific incident.
    Useful for reviewing what was reported via voice.
    """
    from services import supabase
    
    try:
        response = (
            supabase.table("transcripts")
            .select("*")
            .eq("incident_id", incident_id)
            .order("created_at", desc=True)
            .execute()
        )
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500