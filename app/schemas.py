from pydantic import BaseModel, Field
from typing import List, Optional

class CampaignInput(BaseModel):
    user_id: int
    product_description: str = Field(..., min_length=10)
    platform: str
    audience: str
    budget: str

class AdVariant(BaseModel):
    id: int
    angle: str
    headline: str
    caption: str
    cta: str
    hashtags: List[str]
    score: int
    tips: List[str]
    image_url: Optional[str] = None


class CampaignResponse(BaseModel):
    message: str
    campaign_id: int
    platform: str
    audience: str
    budget: str
    variants: List[AdVariant]


class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True