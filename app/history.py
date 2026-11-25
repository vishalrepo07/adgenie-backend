"""
app/history.py

Campaign history API: the user sends their email + name and gets back
their previous campaigns with ad variants.

Endpoint:
    POST /campaigns/history
        body: {"email": "...", "name": "..."}
        query: page, page_size, platform, include_images
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Campaign, User

router = APIRouter(prefix="/campaigns", tags=["History"])


# --------------------------------------------------------------------------
# Schemas
# --------------------------------------------------------------------------
class HistoryRequest(BaseModel):
    email: str
    name: str


def _csv_to_list(v):
    """hashtags/tips are stored as comma-separated strings -> convert to list."""
    if v is None:
        return []
    if isinstance(v, str):
        return [item.strip() for item in v.split(",") if item.strip()]
    return v


class AdVariantOut(BaseModel):
    id: int
    angle: Optional[str] = None
    headline: Optional[str] = None
    caption: Optional[str] = None
    cta: Optional[str] = None
    hashtags: List[str] = []
    score: Optional[int] = None
    tips: List[str] = []
    image_url: Optional[str] = None  # None unless include_images=true
    created_at: datetime

    @field_validator("hashtags", "tips", mode="before")
    @classmethod
    def split_csv(cls, v):
        return _csv_to_list(v)

    model_config = {"from_attributes": True}


class CampaignOut(BaseModel):
    id: int
    product_description: str
    platform: str
    audience: str
    budget: str
    status: str
    created_at: datetime
    ad_variants: List[AdVariantOut] = []

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    user_name: str
    email: str
    total: int
    page: int
    page_size: int
    items: List[CampaignOut]


# --------------------------------------------------------------------------
# Endpoint
# --------------------------------------------------------------------------
@router.post("/history", response_model=HistoryResponse)
def get_campaign_history(
    body: HistoryRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    platform: Optional[str] = None,
    include_images: bool = Query(False, description="Images are large; off by default"),
    db: Session = Depends(get_db),
):
    """Find the user by email + name and return their previous campaigns (newest first)."""
    email = body.email.strip().lower()
    name = body.name.strip().lower()

    user = (
        db.query(User)
        .filter(func.lower(User.email) == email, func.lower(User.name) == name)
        .first()
    )
    # Same message whether the email or the name is wrong, so we don't reveal
    # which emails are registered.
    if not user:
        raise HTTPException(status_code=404, detail="No user found with this email and name")

    query = db.query(Campaign).filter(Campaign.user_id == user.id)
    if platform:
        query = query.filter(Campaign.platform == platform)

    total = query.with_entities(func.count(Campaign.id)).scalar() or 0

    campaigns = (
        query.options(selectinload(Campaign.ad_variants))  # avoids N+1 queries
        .order_by(Campaign.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [CampaignOut.model_validate(c) for c in campaigns]
    if not include_images:
        for item in items:
            for variant in item.ad_variants:
                variant.image_url = None

    return HistoryResponse(
        user_name=user.name,
        email=user.email,
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )