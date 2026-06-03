"""
LocalFlow — SMS service layer (Twilio integration).
"""

from database import insert, get, now


MISSED_CALL_TEMPLATE = (
    "Hi {name}! We noticed you called about {service}. "
    "We're tied up right now but we'd love to help. "
    "Reply with your availability or just say 'BOOK' and we'll get you scheduled!"
)

FOLLOWUP_STEP1 = (
    "Hey {name}, just checking in! Still thinking about your {service} project? "
    "We've got openings this week — reply 'YES' to grab a slot."
)

FOLLOWUP_STEP2 = (
    "Hi {name}, last chance to lock in our special pricing for {service}. "
    "Reply 'GO' and we'll send over a quick estimate!"
)

CONFIRMATION_TEMPLATE = (
    "Confirmed! We'll see you on {scheduled_at} for your {job_type} appointment. "
    "Reply 'RESCHEDULE' if you need to change it."
)

REMINDER_TEMPLATE = (
    "Reminder: You have a {job_type} appointment tomorrow at {scheduled_at}. "
    "Reply 'OK' to confirm or 'RESCHEDULE' to change."
)


def send_sms(to_phone: str, body: str, lead_id: str | None = None) -> dict:
    """
    Send an SMS message.
    Stores in conversations table.
    In production, this would call Twilio API.
    """
    message_id = f"sim_{__import__('uuid').uuid4().hex[:8]}"

    if lead_id:
        insert("conversations", {
            "lead_id": lead_id,
            "direction": "outbound",
            "message_type": "sms",
            "content": body,
            "timestamp": now(),
        })

    return {
        "status": "sent",
        "message_id": message_id,
        "to": to_phone,
        "body": body,
    }


def send_missed_call_sms(lead_id: str, name: str = "there", service: str = "service") -> dict:
    """Send an auto-reply SMS for a missed call."""
    lead = get("leads", lead_id)
    if not lead:
        return {"status": "error", "error": "Lead not found"}

    phone = lead.get("phone")
    if not phone:
        return {"status": "error", "error": "No phone number"}

    body = MISSED_CALL_TEMPLATE.format(name=name or "there", service=service or "service")
