"""
LocalFlow — Smart follow-up sequence engine.
Manages automated follow-up sequences for lead nurturing.
"""

from database import insert, get, list_all, update, now, new_id
from services.sms_service import send_sms, FOLLOWUP_STEP1, FOLLOWUP_STEP2


# ── Sequence Templates ──────────────────────────────────────────

SEQUENCES = {
    "default": {
        "steps": [
            {"delay_hours": 1, "template": FOLLOWUP_STEP1},
            {"delay_hours": 24, "template": FOLLOWUP_STEP2},
            {"delay_hours": 72, "template": "Final check: {name}, are you still interested in {service}? This is our last message unless you reply."},
        ]
    },
    "urgent": {
        "steps": [
            {"delay_hours": 0, "template": "Hi {name}! We got your urgent request for {service}. Call us now at (555) 123-4567!"},
            {"delay_hours": 4, "template": "Quick follow-up: {name}, we're ready to help with your {service} need. Reply to schedule ASAP."},
        ]
    },
    "estimate": {
        "steps": [
            {"delay_hours": 48, "template": "Hi {name}! Just following up on the estimate we sent for your {service} project. Any questions?"},
            {"delay_hours": 168, "template": "Last call: {name}, our estimate for {service} is still valid. Ready to move forward?"},
        ]
    },
}


def trigger_followup(lead_id: str, sequence_type: str = "default") -> dict:
    """
    Trigger a follow-up sequence for a lead.
    Creates the first follow-up step in the database.
    """
    lead = get("leads", lead_id)
    if not lead:
        return {"status": "error", "error": "Lead not found"}

    sequence = SEQUENCES.get(sequence_type, SEQUENCES["default"])
    if not sequence["steps"]:
        return {"status": "error", "error": "No steps in sequence"}

    name = lead.get("name", "there")
    service = lead.get("service_needed", "services")
    phone = lead.get("phone")

    if not phone:
        return {"status": "error", "error": "No phone number"}

    step = sequence["steps"][0]
    body = step["template"].format(name=name, service=service)

    # Create followup record
    followup_id = insert("followups", {
        "lead_id": lead_id,
        "sequence_type": sequence_type,
        "step": 1,
        "scheduled_at": now(),
        "sent": 0,
        "completed": 0,
        "content": body,
    })

    # Send the SMS
    send_sms(phone, body, lead_id)

    # Mark as sent
    update("followups", followup_id, {
        "sent": 1,
        "scheduled_at": now(),
    })

    return {
        "status": "triggered",
        "followup_id": followup_id,
        "step": 1,
        "total_steps": len(sequence["steps"]),
        "body": body,
    }


def advance_followup(followup_id: str) -> dict:
    """
    Advance to the next step in a follow-up sequence.
    """
    followup = get("followups", followup_id)
    if not followup:
        return {"status": "error", "error": "Follow-up not found"}

    lead = get("leads", followup["lead_id"])
    if not lead:
        return {"status": "error", "error": "Lead not found"}

    sequence = SEQUENCES.get(followup.get("sequence_type", "default"), SEQUENCES["default"])
    current_step = followup.get("step", 1)

    if current_step >= len(sequence["steps"]):
        # Sequence complete
        update("followups", followup_id, {"completed": 1})
        return {"status": "complete", "message": "All steps completed"}

    # Move to next step
    next_step = current_step + 1
    step_data = sequence["steps"][next_step - 1]

    name = lead.get("name", "there")
    service = lead.get("service_needed", "services")
    body = step_data["template"].format(name=name, service=service)

    phone = lead.get("phone")
    if phone:
        send_sms(phone, body, lead["id"])

    update("followups", followup_id, {
        "step": next_step,
        "sent": 1,
        "content": body,
        "scheduled_at": now(),
    })

    return {
        "status": "advanced",
        "followup_id": followup_id,
        "step": next_step,
        "total_steps": len(sequence["steps"]),
        "body": body,
    }


def get_pending_followups() -> list[dict]:
    """Get all followups that are not yet completed."""
    return list_all("followups", where="completed = 0", order_by="scheduled_at ASC")


def get_lead_followups(lead_id: str) -> list[dict]:
    """Get all followups for a specific lead."""
