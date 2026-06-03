"""
LocalFlow — Dashboard summary and metrics routes.
"""

from fastapi import APIRouter

from models import DashboardSummary
from database import count, list_all, _run_sql

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary():
    """
    Get aggregated dashboard metrics for the business.
    """
    total_leads = count("leads")
    new_leads_today = count("leads", where="date(created_at) = date('now')")
    booked = count("leads", where="status = 'booked'")
    pending_followups = count("followups", where="completed = 0")
    upcoming_bookings = count("bookings", where="status IN ('confirmed', 'pending')")
    total_content = count("content_ideas")

    # Calculate conversion rate (leads that booked / total leads)
    conversion_rate = round((booked / max(total_leads, 1)) * 100, 1)

    return DashboardSummary(
        total_leads=total_leads,
        new_leads_today=new_leads_today,
        booked=booked,
        conversion_rate=conversion_rate,
        pending_followups=pending_followups,
        upcoming_bookings=upcoming_bookings,
        total_content_generated=total_content,
        avg_response_time_minutes=None,  # Would need actual call data
    )


@router.get("/leads-over-time")
def leads_over_time(days: int = 30):
    """
    Get lead counts grouped by date for charting.
    """
    results = _run_sql(
        f"SELECT date(created_at) as date, COUNT(*) as count "
        f"FROM leads "
        f"WHERE created_at >= date('now', '-{days} days') "
        f"GROUP BY date(created_at) "
        f"ORDER BY date ASC"
    )

    return results


@router.get("/status-breakdown")
def status_breakdown():
    """
    Get lead counts grouped by status.
    """
    results = _run_sql(
        "SELECT status, COUNT(*) as count "
        "FROM leads "
        "GROUP BY status "
        "ORDER BY count DESC"
    )

    return results


@router.get("/recent-activity")
def recent_activity(limit: int = 10):
    """
    Get recent activity (conversations) across all leads.
    """
    return list_all(
        "conversations",
        order_by="timestamp DESC",
        limit=min(limit, 50),
    )