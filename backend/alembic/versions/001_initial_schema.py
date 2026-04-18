"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-18 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        'pfz_zones',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('zone_id', sa.String(100), unique=True, nullable=False),
        sa.Column('state', sa.String(50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('source', sa.String(100), server_default='ml_model_v3.0'),
        sa.Column('polygon', Geometry('POLYGON', srid=4326), nullable=False),
        sa.Column('center', Geometry('POINT', srid=4326), nullable=False),
        sa.Column('species_probability', sa.JSON(), server_default='{}'),
        sa.Column('environmental_factors', sa.JSON(), server_default='{}'),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=False),
        sa.Column('distance_from_shore_km', sa.Float()),
        sa.Column('recommended_boat_type', sa.String(50)),
        sa.Column('safety_status', sa.String(20), server_default='green'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_pfz_state_valid', 'pfz_zones', ['state', 'valid_until'])
    op.create_index('idx_pfz_confidence', 'pfz_zones', ['confidence'], postgresql_ops={'confidence': 'DESC'})
    op.execute("CREATE INDEX IF NOT EXISTS idx_pfz_polygon ON pfz_zones USING GIST (polygon)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_pfz_center ON pfz_zones USING GIST (center)")

    op.create_table(
        'users',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('phone', sa.String(20), unique=True, nullable=False),
        sa.Column('name', sa.String(200)),
        sa.Column('state', sa.String(50)),
        sa.Column('home_location', Geometry('POINT', srid=4326)),
        sa.Column('language', sa.String(10), server_default='mr'),
        sa.Column('subscription_tier', sa.String(20), server_default='free'),
        sa.Column('subscription_expires', sa.DateTime(timezone=True)),
        sa.Column('ai_queries_today', sa.Integer(), server_default='0'),
        sa.Column('ai_queries_reset_date', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_seen', sa.DateTime(timezone=True)),
        sa.Column('fcm_token', sa.String(500)),
        sa.Column('preferences', sa.JSON(), server_default='{}'),
    )
    op.create_index('idx_users_phone', 'users', ['phone'])
    op.create_index('idx_users_state', 'users', ['state'])
    op.execute("CREATE INDEX IF NOT EXISTS idx_users_home ON users USING GIST (home_location)")

    op.create_table(
        'catch_logs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('species', sa.String(200), nullable=False),
        sa.Column('quantity_kg', sa.Float()),
        sa.Column('location', Geometry('POINT', srid=4326)),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('pfz_zone_id', sa.String()),
        sa.Column('weather_conditions', sa.JSON(), server_default='{}'),
        sa.Column('notes', sa.String(500)),
        sa.Column('is_shared', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_catch_user_time', 'catch_logs', ['user_id', 'timestamp'])
    op.execute("CREATE INDEX IF NOT EXISTS idx_catch_geom ON catch_logs USING GIST (location)")

    op.create_table(
        'alerts',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.func.gen_random_uuid().cast(sa.String())),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('state', sa.String(50)),
        sa.Column('severity', sa.String(20), server_default='info'),
        sa.Column('affected_region', Geometry('POLYGON', srid=4326)),
        sa.Column('source', sa.String(100)),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('valid_from', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('valid_until', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_alerts_state', 'alerts', ['state', 'is_active'])
    op.create_index('idx_alerts_type', 'alerts', ['type', 'is_active'])

    op.create_table(
        'marine_protected_areas',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.func.gen_random_uuid().cast(sa.String())),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('state', sa.String(50), nullable=False),
        sa.Column('polygon', Geometry('MULTIPOLYGON', srid=4326), nullable=False),
        sa.Column('protection_level', sa.String(50)),
        sa.Column('rules', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_mpa_geom ON marine_protected_areas USING GIST (polygon)")

    op.create_table(
        'incois_bulletins',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.func.gen_random_uuid().cast(sa.String())),
        sa.Column('bulletin_date', sa.Date(), nullable=False),
        sa.Column('state', sa.String(50)),
        sa.Column('raw_content', sa.Text()),
        sa.Column('parsed_zones', sa.JSON()),
        sa.Column('language', sa.String(10), server_default='en'),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_bulletin_date', 'incois_bulletins', ['bulletin_date', 'state'])

    op.create_table(
        'species',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('names', sa.JSON(), nullable=False),
        sa.Column('scientific_name', sa.String(200)),
        sa.Column('family', sa.String(100)),
        sa.Column('habitat', sa.JSON(), server_default='{}'),
        sa.Column('seasonality', sa.JSON(), server_default='{}'),
        sa.Column('moon_preference', sa.JSON(), server_default='[]'),
        sa.Column('catch_time', sa.JSON(), server_default='[]'),
        sa.Column('sustainable_limit_kg_per_day', sa.Float()),
        sa.Column('is_protected', sa.Boolean(), server_default='false'),
        sa.Column('states', sa.JSON(), server_default='[]'),
    )

    op.create_table(
        'ocean_data',
        sa.Column('id', sa.String(), primary_key=True, server_default=sa.func.gen_random_uuid().cast(sa.String())),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('state', sa.String(50)),
        sa.Column('location', Geometry('POINT', srid=4326)),
        sa.Column('sst', sa.Float()),
        sa.Column('chlorophyll', sa.Float()),
        sa.Column('current_u', sa.Float()),
        sa.Column('current_v', sa.Float()),
        sa.Column('wave_height', sa.Float()),
        sa.Column('wave_period', sa.Float()),
        sa.Column('wind_speed', sa.Float()),
        sa.Column('wind_direction', sa.Float()),
        sa.Column('ssh', sa.Float()),
        sa.Column('source', sa.String(100)),
    )
    op.create_index('idx_ocean_time_state', 'ocean_data', ['timestamp', 'state'])
    op.execute("CREATE INDEX IF NOT EXISTS idx_ocean_geom ON ocean_data USING GIST (location)")

    # Active PFZ zones view
    op.execute("""
        CREATE OR REPLACE VIEW active_pfz_zones AS
        SELECT * FROM pfz_zones
        WHERE valid_until > NOW() AND confidence > 0.5
        ORDER BY confidence DESC
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS active_pfz_zones")
    op.drop_table('ocean_data')
    op.drop_table('species')
    op.drop_table('incois_bulletins')
    op.drop_table('marine_protected_areas')
    op.drop_table('alerts')
    op.drop_table('catch_logs')
    op.drop_table('users')
    op.drop_table('pfz_zones')
