"""
LocalFlow — AI lead qualification and scoring service.
Uses simple rule-based scoring by default.
In production, this would call an LLM (OpenAI, Anthropic, etc.).
"""

from database import get, update, now


# ── Qualification Score Weights ─────────────────────────────────

WEIGHTS = {
    "urgency_high": 30,
    "urgency_medium": 20,
    "urgency_low": 10,
    "has_budget": 25,
    "has_location": 15,
    "has_service": 20,
    "has_email": 10,
    "has_phone": 5,
}


def score_lead(lead_id: str) -> dict:
    """
    Score a lead based on available data fields.
    Returns score dict with total and breakdown.
    """
    lead = get("leads", lead_id)
    if not lead:
        return {"error": "Lead not found", "total": 0}

    breakdown = {}
    total = 0

    # Urgency scoring
    urgency = (lead.get("urgency") or "").lower()
    if urgency == "urgent":
        total += WEIGHTS["urgency_high"]
        breakdown["urgency"] = WEIGHTS["urgency_high"]
    elif urgency == "high":
        total += WEIGHTS["urgency_high"]
        breakdown["urgency"] = WEIGHTS["urgency_high"]
    elif urgency == "medium":
        total += WEIGHTS["urgency_medium"]
        breakdown["urgency"] = WEIGHTS["urgency_medium"]
    elif urgency == "low":
        total += WEIGHTS["urgency_low"]
        breakdown["urgency"] = WEIGHTS["urgency_low"]

    # Data completeness scoring
    if lead.get("budget"):
        total += WEIGHTS["has_budget"]
        breakdown["budget"] = WEIGHTS["has_budget"]

    if lead.get("location"):
        total += WEIGHTS["has_location"]
        breakdown["location"] = WEIGHTS["has_location"]

    if lead.get("service_needed"):
        total += WEIGHTS["has_service"]
        breakdown["service"] = WEIGHTS["has_service"]

    if lead.get("email"):
        total += WEIGHTS["has_email"]
        breakdown["email"] = WEIGHTS["has_email"]

    if lead.get("phone"):
        total += WEIGHTS["has_phone"]
        breakdown["phone"] = WEIGHTS["has_phone"]

    return {"total": total, "breakdown": breakdown, "max_possible": 100}


def qualify_lead(lead_id: str) -> dict:
    """
    Run qualification logic on a lead.
    Updates the lead's ai_summary with qualification insights.
    Returns qualification result.
    """
    score_result = score_lead(lead_id)
    total = score_result["total"]

    if total >= 70:
        status = "qualified"
        summary = f"High-quality lead (score: {total}/100). Complete profile, ready for booking."
    elif total >= 40:
        status = "contacted"
        summary = f"Moderate-quality lead (score: {total}/100). Needs nurturing — gaps in budget, location, or service info."
    else:
        status = "new"
        summary = f"Low-quality lead (score: {total}/100). Minimal data — needs initial outreach."

    update("leads", lead_id, {
        "status": status,
        "ai_summary": summary,
        "updated_at": now(),
    })

    return {
        "lead_id": lead_id,
        "score": score_result,
        "status": status,
        "summary": summary,
    }


def generate_ai_note(lead_id: str, extra_context: str = "") -> str:
    """
    Generate a conversational AI summary for a lead.
    In production, this would call an LLM.
    """
    lead = get("leads", lead_id)
    if not lead:
        return ""

    parts = [f"Lead: {lead.get('name', 'Unknown')}"]
    if lead.get("service_needed"):
        parts.append(f"needs {lead['service_needed']}")
    if lead.get("urgency"):
        parts.append(f"urgency: {lead['urgency']}")
    if lead.get("location"):
        parts.append(f"located in {lead['location']}")
    if lead.get("budget"):
        parts.append(f"budget: {lead['budget']}")

    summary = ". ".join(parts) + "."
    if extra_context:
        summary += f" Additional context: {extra_context}"

    update("leads", lead_id, {
        "ai_summary": summary,
        "updated_at": now(),
    })

