"""
LocalFlow — Pydantic models for API request/response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Lead Models ─────────────────────────────────────────────────

class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = None
    email: Optional[str] = None
    service_needed: Optional[str] = None
    urgency: Optional[str] = Field(None, pattern=r"^(low|medium|high|urgent)$")
    location: Optional[str] = None
    budget: Optional[str] = None
    tags: Optional[str] = ""
    ai_summary: Optional[str] = ""


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    service_needed: Optional[str] = None
    urgency: Optional[str] = Field(None, pattern=r"^(low|medium|high|urgent)$")
    location: Optional[str] = None
    budget: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(new|contacted|qualified|estimating|booked|closed|lost)$")
    tags: Optional[str] = None
    ai_summary: Optional[str] = None


class LeadTagUpdate(BaseModel):
    tags: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(new|contacted|qualified|estimating|booked|closed|lost)$")


class LeadResponse(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    service_needed: Optional[str] = None
    urgency: Optional[str] = None
    location: Optional[str] = None
    budget: Optional[str] = None
    status: str
    tags: Optional[str] = ""
    ai_summary: Optional[str] = ""
    created_at: str
    updated_at: str


# ── Conversation Models ─────────────────────────────────────────

class ConversationCreate(BaseModel):
    lead_id: str
    direction: str = Field(..., pattern=r"^(inbound|outbound)$")
    message_type: str = Field(..., pattern=r"^(sms|call|email|note)$")
    content: str = Field(..., min_length=1)


class ConversationResponse(BaseModel):
    id: str
    lead_id: str
    direction: str
    message_type: str
    content: str
    timestamp: str


# ── Missed Call Model ───────────────────────────────────────────

class MissedCallCreate(BaseModel):
    caller_phone: str = Field(..., min_length=1)
    caller_name: Optional[str] = ""
    called_at: Optional[str] = None


# ── Booking Models ──────────────────────────────────────────────

class BookingCreate(BaseModel):
    lead_id: str
    job_type: Optional[str] = None
    scheduled_at: Optional[str] = None
    notes: Optional[str] = ""


class BookingConfirm(BaseModel):
    confirmed: bool = True


class BookingRemind(BaseModel):
    pass


class BookingResponse(BaseModel):
    id: str
    lead_id: str
    job_type: Optional[str] = None
    scheduled_at: Optional[str] = None
    status: str
    confirmed: int
    reminders_sent: int
    notes: Optional[str] = ""
    created_at: str


# ── Follow-up Models ────────────────────────────────────────────

class FollowupTrigger(BaseModel):
    lead_id: str
    sequence_type: Optional[str] = "default"


class FollowupResponse(BaseModel):
    id: str
    lead_id: str
    sequence_type: Optional[str] = None
    step: int
    scheduled_at: Optional[str] = None
    sent: int
    completed: int
    content: Optional[str] = ""
    created_at: str


# ── Content Idea Models ─────────────────────────────────────────

class ContentIdeaGenerate(BaseModel):
    service_type: str = Field(..., min_length=1)
    platform: Optional[str] = "facebook"
    count: Optional[int] = Field(default=3, ge=1, le=10)


class ContentIdeaResponse(BaseModel):
    id: str
    service_type: Optional[str] = None
    platform: Optional[str] = None
    hook: Optional[str] = None
    caption: Optional[str] = None
    cta: Optional[str] = None
    generated_at: str = ""
    published: int


# ── Dashboard Models ────────────────────────────────────────────

class DashboardSummary(BaseModel):
    total_leads: int
    new_leads_today: int
    booked: int
    conversion_rate: float
    pending_followups: int
    upcoming_bookings: int
    total_content_generated: int
    avg_response_time_minutes: Optional[float] = None


# ── Estimate / Job Flow (lightweight) ───────────────────────────

class EstimateCreate(BaseModel):
    lead_id: str
    amount: Optional[float] = None
    description: Optional[str] = ""
    status: Optional[str] = Field("draft", pattern=r"^(draft|sent|approved|rejected)$")


# ── Calendar Sync (stub) ────────────────────────────────────────

class CalendarSyncRequest(BaseModel):
    booking_id: str
    action: str = Field(..., pattern=r"^(sync|remove)$")