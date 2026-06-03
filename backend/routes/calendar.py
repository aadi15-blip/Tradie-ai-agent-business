"""
LocalFlow — Calendar sync routes (stub/structured).
In production, this integrates with Google Calendar API.
"""

from fastapi import APIRouter, HTTPException

from models import CalendarSyncRequest
from database import get

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])


@router.post("/sync")
def sync_to_calendar(data: CalendarSyncRequest):
    """
    Sync a booking to an external calendar (Google Calendar, etc.).
    This is a structured stub — in production, implement OAuth2 and
    Google Calendar API calls here.
    """
    booking = get("bookings", data.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    lead = get("leads", booking["lead_id"])

    event_data = {
        "summary": f"{booking.get('job_type', 'Service')} - {lead.get('name', 'Client') if lead else 'Client'}",
        "description": f"Lead: {lead.get('name', 'N/A') if lead else 'N/A'}\n"
                       f"Phone: {lead.get('phone', 'N/A') if lead else 'N/A'}\n"
                       f"Notes: {booking.get('notes', '')}",
        "start": booking.get("scheduled_at", ""),
        "end": booking.get("scheduled_at", ""),  # Would calculate duration in production
        "status": booking.get("status", "pending"),
    }

    if data.action == "sync":
        # In production: create Google Calendar event via API
        return {
            "status": "synced",
            "booking_id": data.booking_id,
            "event": event_data,
            "calendar_event_id": f"cal_sim_{data.booking_id[:8]}",
        }
    elif data.action == "remove":
        # In production: delete Google Calendar event via API
        return {
            "status": "removed",
            "booking_id": data.booking_id,
        }

    raise HTTPException(status_code=400, detail="Invalid action")


@router.get("/events")
def list_calendar_events(limit: int = 20):
    """
    List upcoming bookings as calendar events.
    """
    from database import list_all as db_list_all

    bookings = db_list_all(
        "bookings",
        where="status IN ('confirmed', 'pending')",
        order_by="scheduled_at ASC",
        limit=limit,
    )

    events = []
    for booking in bookings:
        lead = get("leads", booking["lead_id"])
        events.append({
            "id": booking["id"],
            "title": f"{booking.get('job_type', 'Service')} - {lead.get('name', 'Client') if lead else 'Client'}",
            "start": booking.get("scheduled_at", ""),
            "status": booking.get("status", ""),
            "lead_name": lead.get("name", "Unknown") if lead else "Unknown",
        })

