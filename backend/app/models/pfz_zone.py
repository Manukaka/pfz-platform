from sqlalchemy import Column, String, Float, DateTime, JSON, Index, text
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from datetime import datetime
import uuid

from ..core.database import Base


class PfzZone(Base):
    __tablename__ = "pfz_zones"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_id = Column(String, unique=True, nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    source = Column(String(100), default="ml_model_v3.0")
    polygon = Column(Geometry("POLYGON", srid=4326), nullable=False)
    center = Column(Geometry("POINT", srid=4326), nullable=False)
    species_probability = Column(JSON, default={})
    environmental_factors = Column(JSON, default={})
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    distance_from_shore_km = Column(Float)
    recommended_boat_type = Column(String(50))
    safety_status = Column(String(20), default="green")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_pfz_state_valid", "state", "valid_until"),
        Index("idx_pfz_geom", "polygon", postgresql_using="gist"),
        Index("idx_pfz_center", "center", postgresql_using="gist"),
        {"timescaledb_hypertable": False},  # TimescaleDB note
    )


class OceanData(Base):
    __tablename__ = "ocean_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    state = Column(String(50), index=True)
    location = Column(Geometry("POINT", srid=4326))
    sst = Column(Float)           # Sea Surface Temperature (°C)
    chlorophyll = Column(Float)   # mg/m³
    current_u = Column(Float)     # m/s eastward
    current_v = Column(Float)     # m/s northward
    wave_height = Column(Float)   # meters
    wind_speed = Column(Float)    # km/h
    wind_direction = Column(Float) # degrees
    source = Column(String(100))

    __table_args__ = (
        Index("idx_ocean_time_state", "timestamp", "state"),
        Index("idx_ocean_geom", "location", postgresql_using="gist"),
    )
