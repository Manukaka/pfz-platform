from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = "DaryaSagar API"
    version: str = "3.0.0"
    environment: str = "development"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://darya:password@localhost:5432/daryasagar"
    database_sync_url: str = "postgresql://darya:password@localhost:5432/daryasagar"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_pfz_ttl: int = 900  # 15 min

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_pfz_topic: str = "pfz-zones"
    kafka_satellite_topic: str = "satellite-updates"
    kafka_alerts_topic: str = "alerts"
    kafka_catches_topic: str = "user-catches"

    # Supabase / Auth
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"

    # Anthropic / Claude
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-4-7"
    claude_cache_ttl: int = 300  # seconds for prompt cache

    # Mapbox
    mapbox_access_token: str = ""

    # INCOIS
    incois_base_url: str = "https://incois.gov.in"

    # ML model paths
    pfz_model_path: str = "models/pfz_model.onnx"
    safety_model_path: str = "models/safety_model.onnx"
    species_model_path: str = "models/species_model.onnx"

    # Sentry
    sentry_dsn: str = ""

    # CORS
    cors_origins: List[str] = ["*"]

    # Rate limiting
    free_tier_ai_queries_per_day: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
