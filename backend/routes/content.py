"""
LocalFlow — Content ideation routes.
Generates and retrieves marketing content ideas.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from models import ContentIdeaGenerate, ContentIdeaResponse
from services.content_engine import generate_content_ideas, get_generated_ideas

router = APIRouter(prefix="/api/content", tags=["Content"])


@router.get("/ideas", response_model=list[ContentIdeaResponse])
def list_content_ideas(
    service_type: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
):
    """Get previously generated content ideas."""
    return get_generated_ideas(service_type=service_type or "", limit=limit)


@router.post("/ideas/generate", status_code=201)
def generate_ideas(data: ContentIdeaGenerate):
    """Generate new content ideas for a service type."""
    if not data.service_type:
        raise HTTPException(status_code=400, detail="service_type is required")

    ideas = generate_content_ideas(
        service_type=data.service_type,
        platform=data.platform or "facebook",
        count=data.count or 3,
    )

    return {
        "service_type": data.service_type,
        "platform": data.platform or "facebook",
        "count": len(ideas),
        "ideas": ideas,
    }


@router.get("/templates")
def list_content_templates():
    """List available content templates by service type."""
    from services.content_engine import CONTENT_TEMPLATES

    result = {}
    for service_type, templates in CONTENT_TEMPLATES.items():
        result[service_type] = {
            "hook_count": len(templates["hooks"]),
            "caption_count": len(templates["captions"]),
            "cta_count": len(templates["ctas"]),
        }

