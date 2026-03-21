# backend/agents/twilio_agent.py
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    NGROK_URL
)
from services import supabase

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def get_responder_for_resource_type(resource_type: str) -> dict:
    response = (
        supabase.table("responders")
        .select("*")
        .eq("resource_type", resource_type)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def log_call(incident_id, resource_id, responder, call_sid):
    supabase.table("call_logs").insert({
        "incident_id": incident_id,
        "resource_id": resource_id,
        "responder_name": responder.get("name"),
        "phone": responder.get("phone"),
        "call_sid": call_sid,
        "status": "initiated"
    }).execute()


def clean_text(text: str) -> str:
    """
    Cleans text for safe use inside TwiML XML.
    Removes characters that could break the XML structure.
    """
    return (
        str(text)
        .replace("'", "")
        .replace("&", "and")
        .replace("<", "")
        .replace(">", "")
        .replace('"', "")
    )


def make_responder_call(
    incident_id: str,
    resource_id: str,
    resource_type: str,
    incident_title: str,
    incident_location: str,
    incident_description: str,
    priority: str
) -> dict:
    """
    Makes a single call to a responder for a specific resource type.
    Reads out full incident details including description.
    """
    responder = get_responder_for_resource_type(resource_type)

    if not responder:
        return {
            "called": False,
            "reason": f"No responder found for {resource_type}"
        }

    webhook_url = f"{NGROK_URL}/api/twilio/response"

    # Clean all text fields before putting them in XML
    c_title       = clean_text(incident_title)
    c_location    = clean_text(incident_location)
    c_description = clean_text(incident_description)
    c_priority    = clean_text(priority)
    c_type        = clean_text(resource_type.replace("_", " "))

    twiml_message = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="1" action="{webhook}" method="POST">
        <Say voice="alice">
            This is Res Q Net Emergency System.
            Alert. A {priority} priority incident has been reported.
            Incident name: {title}.
            Description: {description}.
            Location: {location}.
            You are being dispatched as {resource}.
            Press 1 to confirm your availability.
            Press 2 if you are unavailable.
        </Say>
    </Gather>
    <Say voice="alice">
        We did not receive your response. Please contact dispatch immediately.
    </Say>
</Response>""".format(
        webhook=webhook_url,
        priority=c_priority,
        title=c_title,
        description=c_description,
        location=c_location,
        resource=c_type
    )

    try:
        call = client.calls.create(
            twiml=twiml_message,
            to=responder["phone"],
            from_=TWILIO_PHONE_NUMBER
        )

        log_call(incident_id, resource_id, responder, call.sid)

        return {
            "called": True,
            "responder": responder["name"],
            "phone": responder["phone"],
            "call_sid": call.sid
        }

    except Exception as e:
        return {
            "called": False,
            "reason": str(e)
        }


def call_all_responders(
    incident_id: str,
    assigned_resources: list,
    incident_title: str,
    incident_location: str,
    priority: str,
    incident_description: str = ""
) -> list:
    """
    Makes ONE call per incident regardless of how many resources assigned.
    Summarizes ALL assigned resource types in a single call message.
    Reads out the full incident description.
    """
    if not assigned_resources:
        return []

    # Build summary of all resource types
    resource_types = list(set([r["type"] for r in assigned_resources]))
    resources_text = ", ".join([r.replace("_", " ") for r in resource_types])
    total = len(assigned_resources)

    # Get responder phone from first resource type
    responder = get_responder_for_resource_type(assigned_resources[0]["type"])

    if not responder:
        return [{"called": False, "reason": "No responder found"}]

    webhook_url = f"{NGROK_URL}/api/twilio/response"

    # Clean all fields
    c_title       = clean_text(incident_title)
    c_location    = clean_text(incident_location)
    c_description = clean_text(incident_description)
    c_priority    = clean_text(priority)
    c_resources   = clean_text(f"{total} units including {resources_text}")

    twiml_message = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather numDigits="1" action="{webhook}" method="POST">
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
        We did not receive your response. Please contact dispatch immediately.
    </Say>
</Response>""".format(
        webhook=webhook_url,
        priority=c_priority,
        title=c_title,
        description=c_description,
        location=c_location,
        resources=c_resources
    )

    try:
        call = client.calls.create(
            twiml=twiml_message,
            to=responder["phone"],
            from_=TWILIO_PHONE_NUMBER
        )

        log_call(
            incident_id=incident_id,
            resource_id=assigned_resources[0]["id"],
            responder=responder,
            call_sid=call.sid
        )

        return [{
            "called": True,
            "responder": responder["name"],
            "phone": responder["phone"],
            "call_sid": call.sid,
            "resources_notified": resource_types,
            "total_units": total
        }]

    except Exception as e:
        return [{
            "called": False,
            "reason": str(e)
        }]