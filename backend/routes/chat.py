"""LocalFlow AI Chat Agent route."""
from fastapi import APIRouter, HTTPException
from services.chat_agent import process_message
router = APIRouter(prefix="/api/chat", tags=["Chat Agent"])

@router.post("")
def chat(data: dict):
    msg = data.get("message","").strip()
    sid = data.get("session_id") or data.get("lead_id","new")
    if not msg: raise HTTPException(400,"Message required")
    r = process_message(sid, msg)
    return {
        "session_id": r["lead_id"],
        "response": r["response"],
        "intent": r.get("intent"),
        "service": r.get("service"),
        "lead_complete": r.get("lead_complete",False),
        "lead_info": r.get("lead_info"),
    }