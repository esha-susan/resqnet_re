# backend/agents/speech_agent.py
# THE SPEECH AGENT — Local Whisper Edition
#
# Uses faster-whisper to run OpenAI's Whisper model LOCALLY.
# No API key. No quota. No cost. Same accuracy.
#
# The first time this runs it downloads the model (~150MB).
# Every run after that uses the cached model — very fast.

from faster_whisper import WhisperModel
from services import supabase

# Load the model once when the module is imported.
# "base" is a good balance of speed and accuracy for disaster reports.
# Other options: "tiny" (fastest), "small", "medium", "large" (most accurate)
#
# device="cpu" works on all machines.
# compute_type="int8" makes it faster and uses less RAM.
print("🎙️ Loading Whisper model... (first run downloads ~150MB)")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
print("✅ Whisper model ready")


def transcribe_audio(file_path: str) -> str:
    """
    Transcribes an audio file using the local Whisper model.

    Args:
        file_path: absolute path to the audio file

    Returns:
        full transcript as a single string
    """
    # segments is a generator of transcript chunks
    # info contains language detection and duration
    segments, info = whisper_model.transcribe(
        file_path,
        language="en",        # force English — remove for auto-detect
        beam_size=5           # higher = more accurate, slightly slower
    )

    # Join all segments into one clean transcript string
    transcript = " ".join(segment.text.strip() for segment in segments)
    return transcript


def save_transcript(incident_id: str, transcript_text: str) -> dict:
    """
    Saves a transcript to the database linked to an incident.
    """
    response = (
        supabase.table("transcripts")
        .insert({
            "incident_id": incident_id,
            "transcript_text": transcript_text
        })
        .execute()
    )

    if not response.data:
        raise Exception("Failed to save transcript to database")

    return response.data[0]


def process_audio(file_path: str, incident_id: str = None) -> dict:
    """
    Main entry point for the Speech Agent.
    Transcribes audio and optionally saves to DB.

    Returns:
        { "transcript": "...", "saved": True/False, "transcript_id": "..." }
    """
    # Step 1: Transcribe locally using Whisper
    transcript_text = transcribe_audio(file_path)

    result = {
        "transcript": transcript_text,
        "saved": False,
        "transcript_id": None
    }

    # Step 2: Save to DB if linked to an incident
    if incident_id:
        saved = save_transcript(incident_id, transcript_text)
        result["saved"] = True
        result["transcript_id"] = saved["id"]

    return result