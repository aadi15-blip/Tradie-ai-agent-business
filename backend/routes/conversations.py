"""
LocalFlow — Conversation management routes.
"""

from fastapi import APIRouter, HTTPException

from models import ConversationCreate, ConversationResponse, MissedCallCreate
from database import insert, get, list_all, update, new_id, now
from services.sms_service import send_missed_call_sms

router = APIRouter(prefix="/api", tags=["Conversations"])


@router.post("/leads/{lead_id}/conversation", response_model=ConversationResponse, status_code=201)
def log_conversation(lead_id: str, data: ConversationCreate):
    """Log a conversation message for a lead."""
    lead = get("leads", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    msg_id = insert("conversations", {
        "lead_id": lead_id,
        "direction": data.direction,
        "message_type": data.message_type,
        "content": data.content,
        "timestamp": now(),
    })

    return get("conversations", msg_id)


@router.get("/leads/{lead_id}/conversations", response_model=list[ConversationResponse])
def get_conversations(lead_id: str, limit: int = 50):
    """Get conversation history for a lead."""
    lead = get("leads", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return list_all("conversations", where=f"lead_id = '{lead_id}'", order_by="timestamp ASC", limit=limit)


@router.post("/missed-call")
def handle_missed_call(data: MissedCallCreate):
    """
    Handle a missed call — create or update the lead and send auto-SMS.
    """
    phone = data.caller_phone
    name = data.caller_name or "there"

    # Check if lead exists with this phone number
    existing = list_all("leads", where=f"phone = '{phone}'", limit=1)

    if existing:
        lead_id = existing[0]["id"]
        # Update the lead status to contacted
        update("leads", lead_id, {"status": "contacted", "updated_at": now()})
    else:
        # Create new lead from missed call
        lead_id = insert("leads", {
            "name": name,
            "phone": phone,
            "status": "new",
            "tags": "missed-call",
            "ai_summary": f"Missed call from {phone}",
            "created_at": now(),
            "updated_at": now(),
        })

    # Send auto-reply SMS
    sms_result = send_missed_call_sms(lead_id, name=name, service="services")

    return {
        "lead_id": lead_id,
        "is_new": not bool(existing),
        "sms": sms_result,
    }