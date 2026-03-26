# backend/agents/twilio_agent.py
# THE TWILIO AGENT
#
# Responsibility:
#   - Make automated phone calls to responders
#   - Play incident details via voice
#   - Ask responder to press 1 to confirm or 2 to decline
#   - Log every call attempt in the database
#
# Flow:
#   1. call_all_responders() makes ONE call per incident
#   2. Twilio hits /api/twilio/response when call connects
#   3. Responder presses key
#   4. Twilio hits /api/twilio/handle-input with the digit
#   5. call_logs updated with confirmed/unavailable/no_answer

from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    NGROK_URL
)
from services import supabase

# Initialize Twilio client once
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def get_responder_for_resource_type(resource_type: str) -> dict:
    """
    Finds a responder for a given resource type from the database.
    Returns the first matching responder.
    """
    response = (
        supabase.table("responders")
        .select("*")
        .eq("resource_type", resource_type)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def log_call(incident_id, resource_id, responder, call_sid):
    """
    Saves a call record to call_logs table.
    Status starts as 'initiated' and gets updated
    when responder presses a key via the webhook.
    """
    supabase.table("call_logs").insert({
        "incident_id":    incident_id,
        "resource_id":    resource_id,
        "responder_name": responder.get("name"),
        "phone":          responder.get("phone"),
        "call_sid":       call_sid,
        "status":         "initiated"
    }).execute()


def clean_text(text: str) -> str:
    """
    Cleans text for safe use inside TwiML XML.
    Removes characters that could break XML structure.
    """
    return (
        str(text)
        .replace("'", "")
        .replace("&", "and")
        .replace("<", "")
        .replace(">", "")
        .replace('"', "")
    )


def call_all_responders(
    incident_id: str,
    assigned_resources: list,
    incident_title: str,
    incident_location: str,
    priority: str,
    incident_description: str = ""
) -> list:
    """
    Makes ONE call per incident regardless of how many
    resources are assigned. Summarizes all resource types
    in a single voice message.

    Two-step Twilio flow:
      Step 1: /api/twilio/response  → plays message + waits for keypress
      Step 2: /api/twilio/handle-input → receives digit + updates DB

    Returns list of call results.
    """
    if not assigned_resources:
        return []

    # Build summary of all assigned resource types
    resource_types = list(set([r["type"] for r in assigned_resources]))
    resources_text = ", ".join([r.replace("_", " ") for r in resource_types])
    total = len(assigned_resources)

    # Get responder from first resource type
    responder = get_responder_for_resource_type(assigned_resources[0]["type"])

    if not responder:
        return [{"called": False, "reason": "No responder found"}]

    # Webhook URLs — must be publicly accessible via tunnel
    # Step 1: initial call handler
    response_url = f"{NGROK_URL}/api/twilio/response"
    # Step 2: keypress handler
    handle_url = f"{NGROK_URL}/api/twilio/handle-input"

    # Clean all text fields before putting in XML
    c_title       = clean_text(incident_title)
    c_location    = clean_text(incident_location)
    c_description = clean_text(incident_description)
    c_priority    = clean_text(priority)
    c_resources   = clean_text(f"{total} units including {resources_text}")

    # TwiML — plays message and waits for keypress
    # action points to handle-input which processes the digit
    twiml_message = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="1" action="{handle_url}" method="POST" timeout="10">
        <Say voice="alice">
            This is Res Q Net Emergency System.
            Alert. A {priority} priority incident has been reported.
            Incident name: {title}.
            Description: {description}.
            Location: {location}.
            {resources} have been deployed.
            Press 1 to confirm all units are responding.
            Press 2 if units are unavailable.
        </Say>
    </Gather>
    <Say voice="alice">
        We did not receive your response.
        Please contact dispatch immediately.
    </Say>
</Response>""".format(
        handle_url=handle_url,
        priority=c_priority,
        title=c_title,
        description=c_description,
        location=c_location,
        resources=c_resources
    )

    try:
        # Make the call via Twilio API
        # url parameter tells Twilio where to get TwiML when call connects
        call = client.calls.create(
            twiml=twiml_message,
            to=responder["phone"],
            from_=TWILIO_PHONE_NUMBER
        )

        print(f"📞 Call initiated: {call.sid} → {responder['phone']}")

        # Log the call in database
        log_call(
            incident_id=incident_id,
            resource_id=assigned_resources[0]["id"],
            responder=responder,
            call_sid=call.sid
        )

        return [{
            "called":              True,
            "responder":           responder["name"],
            "phone":               responder["phone"],
            "call_sid":            call.sid,
            "resources_notified":  resource_types,
            "total_units":         total
        }]

    except Exception as e:
        print(f"⚠️ Twilio call failed: {e}")
        return [{
            "called": False,
            "reason": str(e)
        }]