from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, JSON
from geoalchemy2 import Geometry
from datetime import datetime
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200))
    state = Column(String(50), index=True)
    home_location = Column(Geometry("POINT", srid=4326))
    language = Column(String(10), default="mr")
    subscription_tier = Column(String(20), default="free")
    subscription_expires = Column(DateTime)
    ai_queries_today = Column(Integer, default=0)
    ai_queries_reset_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime)
    fcm_token = Column(String(500))
    preferences = Column(JSON, default={})


class CatchLog(Base):
    __tablename__ = "catch_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    species = Column(String(200), nullable=False)
    quantity_kg = Column(Float)
    location = Column(Geometry("POINT", srid=4326))
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    pfz_zone_id = Column(String)
    weather_conditions = Column(JSON, default={})
    notes = Column(String(500))
    is_shared = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
