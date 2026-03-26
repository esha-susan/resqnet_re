# backend/routes/twilio_webhook.py
from flask import Blueprint, request, Response, jsonify
from services import supabase

twilio_bp = Blueprint('twilio', __name__, url_prefix='/api/twilio')


@twilio_bp.route('/response', methods=['POST'])
def initial_call():
    """
    Step 1: Twilio calls this when the responder picks up.
    Plays the emergency message and waits for keypress.
    """
    call_sid = request.form.get('CallSid', '')
    print(f"🔥 Twilio webhook hit — CallSid: {call_sid}")

    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="1" action="/api/twilio/handle-input" method="POST" timeout="10">
        <Say voice="alice">
            This is an emergency alert from Res Q Net.
            Press 1 to confirm availability.
            Press 2 if you are unavailable.
        </Say>
    </Gather>
    <Hangup/>
</Response>"""

    return Response(twiml, mimetype='text/xml', status=200)


@twilio_bp.route('/handle-input', methods=['POST'])
def handle_response():
    """
    Step 2: Twilio calls this when responder presses a key.
    Updates call_logs with confirmed/unavailable/no_answer.
    """
    digits   = request.form.get('Digits', '')
    call_sid = request.form.get('CallSid', '')
    print(f"🔥 Keypress received — Digits: {digits} CallSid: {call_sid}")

    if digits == '1':
        status  = 'confirmed'
        message = 'Thank you for confirming. Please proceed to the incident location immediately. Stay safe.'
    elif digits == '2':
        status  = 'unavailable'
        message = 'You have been marked as unavailable. Dispatch will assign another unit.'
    else:
        status  = 'no_answer'
        message = 'No input received. Please contact dispatch directly.'

    # Update call log in database
    if call_sid:
        try:
            supabase.table("call_logs").update({
                "status": status
            }).eq("call_sid", call_sid).execute()
            print(f"✅ Call {call_sid} marked as {status}")
        except Exception as e:
            print(f"⚠️ DB update error: {e}")

    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{}</Say>
    <Hangup/>
</Response>""".format(message)

    return Response(twiml, mimetype='text/xml', status=200)


@twilio_bp.route('/call-logs/<incident_id>', methods=['GET'])
def get_call_logs(incident_id):
    """Returns all call logs for a specific incident."""
    try:
        response = (
            supabase.table("call_logs")
            .select("*")
            .eq("incident_id", incident_id)
            .order("created_at", desc=True)
            .execute()
        )
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500