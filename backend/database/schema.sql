-- DaryaSagar Database Schema
-- PostgreSQL + PostGIS + TimescaleDB

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- PFZ ZONES TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS pfz_zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone_id VARCHAR(100) UNIQUE NOT NULL,
    state VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    source VARCHAR(100) DEFAULT 'ml_model_v3.0',
    polygon GEOMETRY(POLYGON, 4326) NOT NULL,
    center GEOMETRY(POINT, 4326) NOT NULL,
    species_probability JSONB DEFAULT '{}'::jsonb,
    environmental_factors JSONB DEFAULT '{}'::jsonb,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ NOT NULL,
    distance_from_shore_km FLOAT,
    recommended_boat_type VARCHAR(50),
    safety_status VARCHAR(20) DEFAULT 'green',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Spatial index on polygon and center
CREATE INDEX IF NOT EXISTS idx_pfz_polygon ON pfz_zones USING GIST (polygon);
CREATE INDEX IF NOT EXISTS idx_pfz_center ON pfz_zones USING GIST (center);
CREATE INDEX IF NOT EXISTS idx_pfz_state_valid ON pfz_zones (state, valid_until);
CREATE INDEX IF NOT EXISTS idx_pfz_confidence ON pfz_zones (confidence DESC);

-- ==============================================
-- OCEAN DATA - TimescaleDB hypertable
-- ==============================================
CREATE TABLE IF NOT EXISTS ocean_data (
    id UUID DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL,
    state VARCHAR(50),
    location GEOMETRY(POINT, 4326),
    sst FLOAT,           -- Sea Surface Temperature (°C)
    chlorophyll FLOAT,   -- mg/m³
    current_u FLOAT,     -- m/s eastward
    current_v FLOAT,     -- m/s northward
    wave_height FLOAT,   -- meters
    wave_period FLOAT,   -- seconds
    wind_speed FLOAT,    -- km/h
    wind_direction FLOAT, -- degrees
    ssh FLOAT,           -- Sea Surface Height anomaly (m)
    source VARCHAR(100),
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('ocean_data', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_ocean_time_state ON ocean_data (timestamp DESC, state);
CREATE INDEX IF NOT EXISTS idx_ocean_geom ON ocean_data USING GIST (location);

-- Retention policy: keep 2 years of hourly data
SELECT add_retention_policy('ocean_data', INTERVAL '2 years', if_not_exists => TRUE);

-- ==============================================
-- USERS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200),
    state VARCHAR(50),
    home_location GEOMETRY(POINT, 4326),
    language VARCHAR(10) DEFAULT 'mr',
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_expires TIMESTAMPTZ,
    ai_queries_today INT DEFAULT 0,
    ai_queries_reset_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ,
    fcm_token VARCHAR(500),
    preferences JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_users_phone ON users (phone);
CREATE INDEX IF NOT EXISTS idx_users_state ON users (state);
CREATE INDEX IF NOT EXISTS idx_users_home ON users USING GIST (home_location);

-- ==============================================
-- CATCH LOGS TABLE - TimescaleDB hypertable
-- ==============================================
CREATE TABLE IF NOT EXISTS catch_logs (
    id UUID DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL,
    species VARCHAR(200) NOT NULL,
    quantity_kg FLOAT,
    location GEOMETRY(POINT, 4326),
    timestamp TIMESTAMPTZ NOT NULL,
    pfz_zone_id VARCHAR(100),
    weather_conditions JSONB DEFAULT '{}'::jsonb,
    notes VARCHAR(500),
    is_shared BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, timestamp)
);

SELECT create_hypertable('catch_logs', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_catch_user_time ON catch_logs (user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_catch_geom ON catch_logs USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_catch_species ON catch_logs (species);

-- ==============================================
-- ALERTS TABLE
-- ==============================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL,  -- cyclone, warning, pfz, tsunami
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    state VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'info',  -- green, yellow, red, black
    affected_region GEOMETRY(POLYGON, 4326),
    source VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_state ON alerts (state, is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts (type, is_active);

-- ==============================================
-- MARINE PROTECTED AREAS (MPA) - Static
-- ==============================================
CREATE TABLE IF NOT EXISTS marine_protected_areas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    state VARCHAR(50) NOT NULL,
    polygon GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    protection_level VARCHAR(50),
    rules TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mpa_geom ON marine_protected_areas USING GIST (polygon);
CREATE INDEX IF NOT EXISTS idx_mpa_state ON marine_protected_areas (state);

-- ==============================================
-- INCOIS PFZ BULLETINS - Official records
-- ==============================================
CREATE TABLE IF NOT EXISTS incois_bulletins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bulletin_date DATE NOT NULL,
    state VARCHAR(50),
    raw_content TEXT,
    parsed_zones JSONB,
    language VARCHAR(10) DEFAULT 'en',
    fetched_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bulletin_date ON incois_bulletins (bulletin_date DESC, state);

-- ==============================================
-- SPECIES DATABASE
-- ==============================================
CREATE TABLE IF NOT EXISTS species (
    id VARCHAR(100) PRIMARY KEY,
    names JSONB NOT NULL,  -- {mr: "...", gu: "...", etc}
    scientific_name VARCHAR(200),
    family VARCHAR(100),
    habitat JSONB DEFAULT '{}'::jsonb,
    seasonality JSONB DEFAULT '{}'::jsonb,
    moon_preference JSONB DEFAULT '[]'::jsonb,
    catch_time JSONB DEFAULT '[]'::jsonb,
    sustainable_limit_kg_per_day FLOAT,
    is_protected BOOLEAN DEFAULT FALSE,
    states JSONB DEFAULT '[]'::jsonb
);

-- ==============================================
-- VIEWS
-- ==============================================

-- Active PFZ zones view
CREATE OR REPLACE VIEW active_pfz_zones AS
SELECT *
FROM pfz_zones
WHERE valid_until > NOW()
  AND confidence > 0.5
ORDER BY confidence DESC;

-- Recent catches community view
CREATE OR REPLACE VIEW community_catches AS
SELECT
    ST_X(location::geometry) as lon,
    ST_Y(location::geometry) as lat,
    species,
    state,
    DATE_TRUNC('hour', timestamp) as hour_slot,
    AVG(quantity_kg) as avg_kg,
    COUNT(*) as catch_count
FROM catch_logs
WHERE is_shared = TRUE
  AND timestamp > NOW() - INTERVAL '7 days'
  AND location IS NOT NULL
GROUP BY lon, lat, species, state, hour_slot;

COMMENT ON TABLE pfz_zones IS 'Potential Fishing Zones - ML predicted + INCOIS official';
COMMENT ON TABLE ocean_data IS 'TimescaleDB hypertable for ocean parameter time-series';
COMMENT ON TABLE catch_logs IS 'TimescaleDB hypertable for user catch records';
