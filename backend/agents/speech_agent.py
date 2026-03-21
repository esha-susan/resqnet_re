# backend/agents/speech_agent.py
from faster_whisper import WhisperModel
from services import supabase

print("🎙️ Loading Whisper model... (first run downloads ~150MB)")
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
print("✅ Whisper model ready")


def transcribe_audio(file_path: str) -> str:
    segments, info = whisper_model.transcribe(
        file_path,
        language="en",
        beam_size=5
    )
    transcript = " ".join(segment.text.strip() for segment in segments)
    return transcript


def save_transcript(incident_id: str, transcript_text: str) -> dict:
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
    transcript_text = transcribe_audio(file_path)

    result = {
        "transcript": transcript_text,
        "saved": False,
        "transcript_id": None
    }

    if incident_id:
        saved = save_transcript(incident_id, transcript_text)
        result["saved"] = True
        result["transcript_id"] = saved["id"]

    return result