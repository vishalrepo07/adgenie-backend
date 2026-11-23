from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.dialects.mysql import LONGTEXT

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campaigns = relationship("Campaign", back_populates="owner", cascade="all, delete-orphan")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    product_description = Column(Text, nullable=False)
    platform = Column(String(50), nullable=False)
    audience = Column(String(255), nullable=False)
    budget = Column(String(50), nullable=False)

    status = Column(String(20), default="completed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="campaigns")
    ad_variants = relationship("AdVariant", back_populates="campaign", cascade="all, delete-orphan")


class AdVariant(Base):
    __tablename__ = "ad_variants"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)

    angle = Column(String(100), nullable=True)
    headline = Column(String(255), nullable=True)
    caption = Column(Text, nullable=True)
    cta = Column(String(255), nullable=True)
    hashtags = Column(Text, nullable=True)   # store as comma-separated string
    score = Column(Integer, nullable=True)
    tips = Column(Text, nullable=True)       # store as comma-separated string
    image_url = Column(LONGTEXT, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign", back_populates="ad_variants")