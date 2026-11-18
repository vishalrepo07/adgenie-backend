from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.schemas import CampaignInput, CampaignResponse
from app.services.ai_campaign_generator import generate_ai_campaign
from app.services.ai_image_generator import generate_ad_image
from app.models import Campaign, AdVariant
from app import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AdGenie Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.get("/")
def read_root():
    return {"message": "AdGenie backend running"}


@app.post("/api/campaigns/generate", response_model=CampaignResponse)
def generate_campaign(data: CampaignInput, db: Session = Depends(get_db)):
    variants_raw = generate_ai_campaign(data)

    new_campaign = Campaign(
        user_id=data.user_id,
        product_description=data.product_description,
        platform=data.platform,
        audience=data.audience,
        budget=data.budget,
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    for v in variants_raw:
        image_url = generate_ad_image(v["headline"], data.product_description)

        ad_variant = AdVariant(
            campaign_id=new_campaign.id,
            angle=v["angle"],
            headline=v["headline"],
            caption=v["caption"],
            cta=v["cta"],
            hashtags=",".join(v["hashtags"]),
            score=v["score"],
            tips=",".join(v["tips"]),
            image_url=image_url,
        )
        db.add(ad_variant)
        v["image_url"] = image_url
    db.commit()

    return CampaignResponse(
        message="Campaign generated and saved successfully",
        campaign_id=new_campaign.id,
        platform=data.platform,
        audience=data.audience,
        budget=data.budget,
        variants=variants_raw,
    )


@app.get("/api/campaigns/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {
        "id": campaign.id,
        "product_description": campaign.product_description,
        "platform": campaign.platform,
        "audience": campaign.audience,
        "budget": campaign.budget,
        "created_at": campaign.created_at,
        "variants": [
            {
                "id": v.id,
                "angle": v.angle,
                "headline": v.headline,
                "caption": v.caption,
                "cta": v.cta,
                "hashtags": v.hashtags.split(",") if v.hashtags else [],
                "score": v.score,
                "tips": v.tips.split(",") if v.tips else [],
                "image_url": v.image_url,
            }
            for v in campaign.ad_variants
        ],
    }