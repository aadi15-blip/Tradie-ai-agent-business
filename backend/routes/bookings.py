"""
LocalFlow — Booking/appointment scheduling routes.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from models import BookingCreate, BookingConfirm, BookingResponse
from database import insert, get, list_all, update, new_id, now
from services.sms_service import send_sms, CONFIRMATION_TEMPLATE, REMINDER_TEMPLATE

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse, status_code=201)
def create_booking(data: BookingCreate):
    """Create a new booking for a lead."""
    lead = get("leads", data.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    booking_id = insert("bookings", {
        "lead_id": data.lead_id,
        "job_type": data.job_type or "",
        "scheduled_at": data.scheduled_at or "",
        "status": "pending",
        "confirmed": 0,
        "reminders_sent": 0,
        "notes": data.notes or "",
    })

    # Update lead status to estimating/booked
    update("leads", data.lead_id, {
        "status": "booked",
        "updated_at": now(),
    })

    return get("bookings", booking_id)


@router.get("", response_model=list[BookingResponse])
def list_bookings(
    status: Optional[str] = Query(None),
    lead_id: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
):
    """List bookings with optional filters."""
    where_parts = []
    if status:
        where_parts.append(f"status = '{status}'")
    if lead_id:
        where_parts.append(f"lead_id = '{lead_id}'")

    where = " AND ".join(where_parts) if where_parts else ""
    return list_all("bookings", where=where, order_by="scheduled_at ASC", limit=limit)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: str):
    """Get a single booking."""
    booking = get("bookings", booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/{booking_id}/confirm", response_model=BookingResponse)
def confirm_booking(booking_id: str, data: BookingConfirm):
    """Confirm a booking and send confirmation SMS."""
    booking = get("bookings", booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    update("bookings", booking_id, {
        "confirmed": 1 if data.confirmed else 0,
        "status": "confirmed" if data.confirmed else "pending",
    })

    # Send confirmation SMS
    if data.confirmed:
        lead = get("leads", booking["lead_id"])
        if lead and lead.get("phone"):
            body = CONFIRMATION_TEMPLATE.format(
                scheduled_at=booking.get("scheduled_at", "TBD"),
                job_type=booking.get("job_type", "service"),
            )
            send_sms(lead["phone"], body, booking["lead_id"])

    return get("bookings", booking_id)


@router.post("/{booking_id}/remind")
def send_reminder(booking_id: str):
    """Send a reminder SMS for an upcoming booking."""
    booking = get("bookings", booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    lead = get("leads", booking["lead_id"])
    if not lead or not lead.get("phone"):
        raise HTTPException(status_code=400, detail="Lead has no phone number")

    body = REMINDER_TEMPLATE.format(
        scheduled_at=booking.get("scheduled_at", "TBD"),
        job_type=booking.get("job_type", "service"),
    )

    sms_result = send_sms(lead["phone"], body, booking["lead_id"])

    # Increment reminders_sent
    update("bookings", booking_id, {
        "reminders_sent": (booking.get("reminders_sent") or 0) + 1,
    })

    return {
        "booking_id": booking_id,
        "sms": sms_result,
        "reminders_sent": (booking.get("reminders_sent") or 0) + 1,
    }


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: str, data: BookingCreate):
    """Update a booking's details."""
    booking = get("bookings", booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    update_data = {}
    if data.job_type is not None:
        update_data["job_type"] = data.job_type
    if data.scheduled_at is not None:
        update_data["scheduled_at"] = data.scheduled_at
    if data.notes is not None:
        update_data["notes"] = data.notes

    if update_data:
        update("bookings", booking_id, update_data)

