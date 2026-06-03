"""
LocalFlow — Estimate/job flow routes.
Lightweight estimate management for local service businesses.
"""

from fastapi import APIRouter, HTTPException

from models import EstimateCreate
from database import insert, get, list_all, update, new_id, now

router = APIRouter(prefix="/api/estimates", tags=["Estimates"])


# Reuse the leads table's ai_summary for estimates tracking, plus a simple
# in-memory estimate store via a new table or structured notes.
# For simplicity, we store estimates as a JSON string in a new table.

import json


@router.post("", status_code=201)
def create_estimate(data: EstimateCreate):
    """Create a new estimate for a lead."""
    lead = get("leads", data.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Store estimate in a structured format
    estimate_id = new_id()
    estimate_data = {
        "id": estimate_id,
        "lead_id": data.lead_id,
        "amount": data.amount,
        "description": data.description,
        "status": data.status,
        "created_at": now(),
    }

    # We'll store as a note in the conversations table for now
    insert("conversations", {
        "lead_id": data.lead_id,
        "direction": "outbound",
        "message_type": "note",
        "content": f"ESTIMATE|{json.dumps(estimate_data)}",
    })

    # Update lead status to estimating
    update("leads", data.lead_id, {
        "status": "estimating",
        "updated_at": now(),
    })

    return estimate_data


@router.get("/lead/{lead_id}")
def get_lead_estimates(lead_id: str):
    """Get all estimates for a lead."""
    lead = get("leads", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    conversations = list_all(
        "conversations",
        where=f"lead_id = '{lead_id}' AND message_type = 'note' AND content LIKE 'ESTIMATE|%'",
        order_by="timestamp DESC",
    )

    estimates = []
    for conv in conversations:
        try:
            content = conv["content"]
            if content.startswith("ESTIMATE|"):
                data = json.loads(content[9:])
                estimates.append(data)
        except (json.JSONDecodeError, IndexError):
            continue

    return estimates


@router.put("/{estimate_id}/status")
def update_estimate_status(estimate_id: str, status: str):
    """Update the status of an estimate (draft/sent/approved/rejected)."""
    valid_statuses = ["draft", "sent", "approved", "rejected"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {', '.join(valid_statuses)}")

    # Find and update the estimate by searching conversations
    # In a production system, estimates would have their own table
    conversations = list_all(
        "conversations",
        where=f"content LIKE 'ESTIMATE|%'",
        order_by="timestamp DESC",
        limit=100,
    )

    for conv in conversations:
        try:
            content = conv["content"]
            if content.startswith("ESTIMATE|"):
                data = json.loads(content[9:])
                if data.get("id") == estimate_id:
                    # Update estimate data
                    data["status"] = status
                    update("conversations", conv["id"], {
                        "content": f"ESTIMATE|{json.dumps(data)}",
                    })

                    # If approved, update lead status
                    if status == "approved":
                        update("leads", data["lead_id"], {
                            "status": "booked",
                            "updated_at": now(),
                        })

                    return data
        except (json.JSONDecodeError, IndexError):
            continue

