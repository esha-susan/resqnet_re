from flask import Blueprint, request, Response, jsonify
from services import supabase

twilio_bp = Blueprint('twilio', __name__, url_prefix='/api/twilio')


# ✅ STEP 1: Initial call (no double speaking)
@twilio_bp.route('/response', methods=['POST'])
def initial_call():
    call_sid = request.form.get('CallSid', '')

    print(f"🔥 Initial Twilio webhook hit: {call_sid}")

    # ✅ Prevent duplicate execution
    if hasattr(initial_call, "last_sid") and initial_call.last_sid == call_sid:
        print("⚠️ Duplicate call detected, ignoring")
        return Response(
            '<?xml version="1.0"?><Response></Response>',
            mimetype='text/xml'
        )

    initial_call.last_sid = call_sid

    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather 
        numDigits="1" 
        action="/api/twilio/handle-input" 
        method="POST"
        timeout="5"
    >
        <Say voice="alice">
            This is an emergency alert. Press 1 to confirm availability. Press 2 if unavailable.
        </Say>
    </Gather>
    <Hangup/>
</Response>"""

    return Response(twiml, mimetype='text/xml')
# ✅ STEP 2: Handle keypad input (including no input)
@twilio_bp.route('/handle-input', methods=['POST'])
def handle_response():
    print("🔥 Twilio input received")

    digits   = request.form.get('Digits', '')
    call_sid = request.form.get('CallSid', '')

    if digits == '1':
        status  = 'confirmed'
        message = 'Thank you for confirming. Please proceed to the incident location immediately. Stay safe.'
    elif digits == '2':
        status  = 'unavailable'
        message = 'You have been marked as unavailable. Dispatch will assign another unit.'
    else:
        status  = 'no_answer'
        message = 'No input received. Goodbye.'

    # ✅ Update DB safely
    if call_sid:
        try:
            supabase.table("call_logs").update({
                "status": status
            }).eq("call_sid", call_sid).execute()
        except Exception as e:
            print(f"⚠️ DB error: {e}")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{message}</Say>
    <Hangup/>
</Response>"""

    return Response(twiml, mimetype='text/xml', status=200)


# ✅ Existing API (unchanged)
@twilio_bp.route('/call-logs/<incident_id>', methods=['GET'])
def get_call_logs(incident_id):
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