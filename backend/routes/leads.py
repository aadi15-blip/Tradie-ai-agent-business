"""
LocalFlow — Lead capture, qualification, and management routes.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from models import LeadCreate, LeadUpdate, LeadTagUpdate, LeadResponse
from database import insert, get, list_all, update, new_id, now
from services.qualification import qualify_lead

router = APIRouter(prefix="/api/leads", tags=["Leads"])


@router.post("", response_model=LeadResponse, status_code=201)
def create_lead(data: LeadCreate):
    """Capture a new lead."""
    lead_id = new_id()
    insert("leads", {
        "id": lead_id,
        "name": data.name,
        "phone": data.phone or "",
        "email": data.email or "",
        "service_needed": data.service_needed or "",
        "urgency": data.urgency or "",
        "location": data.location or "",
        "budget": data.budget or "",
        "status": "new",
        "tags": data.tags or "",
        "ai_summary": data.ai_summary or "",
        "created_at": now(),
        "updated_at": now(),
    })

    # Auto-qualify the lead
    qualify_lead(lead_id)

    lead = get("leads", lead_id)
    return lead


@router.get("", response_model=list[LeadResponse])
def list_leads(
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100, le=200),
):
    """List leads with optional filters."""
    where_parts = []
    if status:
        where_parts.append(f"status = '{status}'")
    if date_from:
        where_parts.append(f"created_at >= '{date_from}'")
    if date_to:
        where_parts.append(f"created_at <= '{date_to}'")

    where = " AND ".join(where_parts) if where_parts else ""
    return list_all("leads", where=where, order_by="created_at DESC", limit=limit)


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: str):
    """Get a single lead with full details."""
    lead = get("leads", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}/tag", response_model=LeadResponse)
def update_lead_tags(lead_id: str, data: LeadTagUpdate):
    """Update a lead's tags and/or status."""
    lead = get("leads", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = {}
    if data.tags is not None:
        update_data["tags"] = data.tags
    if data.status is not None:
        update_data["status"] = data.status

    if update_data:
        update_data["updated_at"] = now()
        update("leads", lead_id, update_data)

    return get("leads", lead_id)


@router.post("/{lead_id}/qualify")
def qualify_lead_endpoint(lead_id: str):
    """Run AI qualification on a lead."""
    lead = get("leads", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    result = qualify_lead(lead_id)
    return result


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: str, data: LeadUpdate):
    """Update a lead's fields."""
    lead = get("leads", lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = data.model_dump(exclude_none=True)
    if update_data:
        update_data["updated_at"] = now()
        update("leads", lead_id, update_data)

    return get("leads", lead_id)