"""
LocalFlow — Content ideation engine.
Generates marketing content ideas for local service businesses.
Uses template-based generation by default; in production would use an LLM.
"""

from database import insert, list_all, new_id


# ── Content Templates ───────────────────────────────────────────

CONTENT_TEMPLATES = {
    "roofing": {
        "hooks": [
            "Is your roof ready for the next storm?",
            "5 signs you need a roof replacement (not just a repair)",
            "How much does a new roof actually cost?",
            "Don't let a leak ruin your weekend — call us!",
            "We fixed this roof in 1 day. Here's how.",
        ],
        "captions": [
            "Your home deserves the best protection. Our team installs quality roofing that lasts for decades. Free estimates — no pressure, just honest advice.",
            "Storm season is coming. Don't wait until water damage shows up inside your home. Schedule a free roof inspection today.",
            "From leak repair to full replacement, we handle it all. Licensed, insured, and trusted by homeowners across the area.",
            "Your neighbors trust us for a reason. 200+ 5-star reviews and counting. See why homeowners choose LocalFlow Roofing.",
        ],
        "ctas": [
            "Get your free estimate →",
            "Schedule inspection now →",
            "Call us for a quote →",
            "Book your free roof check →",
        ],
    },
    "plumbing": {
        "hooks": [
            "That dripping faucet is costing you money.",
            "Emergency plumber? We're there in 30 minutes.",
            "3 things that wreck your pipes (and how to avoid them)",
            "The #1 cause of burst pipes in winter",
            "Why your water bill spiked (and how to fix it)",
        ],
        "captions": [
            "From dripping faucets to burst pipes, we handle all plumbing emergencies. Fast response, fair pricing, guaranteed work.",
            "Don't let a small leak become a big problem. Our licensed plumbers diagnose and fix issues fast. Same-day service available!",
            "Water heater acting up? We install and repair all brands. Call us before you're left with a cold shower!",
        ],
        "ctas": [
            "Book a plumber now →",
            "Get same-day service →",
            "Schedule your repair →",
            "Call for emergency service →",
        ],
    },
    "hvac": {
        "hooks": [
            "Is your AC ready for summer?",
            "Why your energy bill is so high (hint: it's your HVAC)",
            "3 signs your furnace needs replacing",
            "The ideal temperature for your home (and how to save money)",
            "Don't wait until your AC dies in a heatwave",
        ],
        "captions": [
            "Keep your home comfortable year-round with professional HVAC service. Installation, repair, and maintenance — we do it all.",
            "Beat the heat (and the cold) with a well-maintained HVAC system. Schedule your seasonal tune-up today!",
            "New system installation? We help you choose the right size and efficiency for your home. Save up to 30% on energy bills.",
        ],
        "ctas": [
            "Schedule a tune-up →",
            "Get your free quote →",
            "Book a service call →",
            "Call for emergency HVAC →",
        ],
    },
    "general": {
        "hooks": [
            "Need a reliable local contractor?",
            "We respond in minutes, not days.",
            "Quality work at fair prices — that's our promise.",
            "Your project, our expertise. Let's build something great.",
            "From small repairs to big projects, we've got you covered.",
        ],
        "captions": [
            "Local, trusted, and professional. We treat your home like it's our own. Free estimates on all projects.",
            "Don't trust your home to just anyone. We're licensed, insured, and reviewed by hundreds of happy customers.",
            "Quick response, quality work, and clear communication. That's the LocalFlow difference.",
        ],
        "ctas": [
            "Get a free estimate →",
            "Book your service now →",
            "Call us today →",
            "Schedule a consultation →",
        ],
    },
}


def generate_content_ideas(service_type: str, platform: str = "facebook", count: int = 3) -> list[dict]:
    """
    Generate content ideas for a given service type and platform.
    """
    templates = CONTENT_TEMPLATES.get(service_type.lower(), CONTENT_TEMPLATES["general"])
    import random

    ideas = []
    used_indices = set()

    for _ in range(min(count, 5)):
        hook_idx = random.randint(0, len(templates["hooks"]) - 1)
        caption_idx = random.randint(0, len(templates["captions"]) - 1)
        cta_idx = random.randint(0, len(templates["ctas"]) - 1)

        # Avoid exact duplicates
        key = (hook_idx, caption_idx, cta_idx)
        if key in used_indices:
            continue
        used_indices.add(key)

        idea_id = new_id()
        hook = templates["hooks"][hook_idx]
        caption = templates["captions"][caption_idx]
        cta = templates["ctas"][cta_idx]

        insert("content_ideas", {
            "id": idea_id,
            "service_type": service_type,
            "platform": platform,
            "hook": hook,
            "caption": caption,
            "cta": cta,
        })

        ideas.append({
            "id": idea_id,
            "service_type": service_type,
            "platform": platform,
            "hook": hook,
            "caption": caption,
            "cta": cta,
        })

    return ideas


def get_generated_ideas(service_type: str = "", limit: int = 20) -> list[dict]:
    """Get previously generated content ideas."""
    where = f"service_type = '{service_type}'" if service_type else ""
    return list_all("content_ideas", where=where, order_by="generated_at DESC", limit=limit)
