# backend/routes/twilio_webhook.py
from flask import Blueprint, request, Response, jsonify
from services import supabase

twilio_bp = Blueprint('twilio', __name__, url_prefix='/api/twilio')


@twilio_bp.route('/response', methods=['POST'])
def handle_response():
    """
    Called by Twilio when responder presses a key.
    Digits: 1 = confirmed, 2 = unavailable
    """
    digits = request.form.get('Digits', '')
    call_sid = request.form.get('CallSid', '')

    if digits == '1':
        status = 'confirmed'
        message = 'Thank you for confirming. Please proceed to the incident location immediately. Stay safe.'
    elif digits == '2':
        status = 'unavailable'
        message = 'You have been marked as unavailable. Dispatch will assign another unit.'
    else:
        status = 'no_answer'
        message = 'Invalid response received. Please contact dispatch directly.'

    # Update call log
    if call_sid:
        supabase.table("call_logs").update({
            "status": status
        }).eq("call_sid", call_sid).execute()

    twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{}</Say>
    <Hangup/>
</Response>""".format(message)

    return Response(twiml_response, mimetype='text/xml')


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

