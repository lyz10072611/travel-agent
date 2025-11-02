"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建用户表
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('nickname', sa.String(length=50), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 创建用户偏好表
    op.create_table('user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('daily_distance_min', sa.String(length=20), nullable=True),
        sa.Column('daily_distance_max', sa.String(length=20), nullable=True),
        sa.Column('preferred_route_type', sa.String(length=50), nullable=True),
        sa.Column('avoid_highway', sa.Boolean(), nullable=True),
        sa.Column('night_riding', sa.Boolean(), nullable=True),
        sa.Column('accommodation_type', sa.String(length=50), nullable=True),
        sa.Column('accommodation_budget_min', sa.String(length=20), nullable=True),
        sa.Column('accommodation_budget_max', sa.String(length=20), nullable=True),
        sa.Column('cuisine_preference', sa.JSON(), nullable=True),
        sa.Column('meal_budget_min', sa.String(length=20), nullable=True),
        sa.Column('meal_budget_max', sa.String(length=20), nullable=True),
        sa.Column('equipment_level', sa.String(length=20), nullable=True),
        sa.Column('safety_priority', sa.String(length=20), nullable=True),
        sa.Column('travel_style', sa.String(length=50), nullable=True),
        sa.Column('group_size', sa.String(length=20), nullable=True),
        sa.Column('season_preference', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=False)

    # 创建旅行表
    op.create_table('trips',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_location', sa.String(length=100), nullable=False),
        sa.Column('end_location', sa.String(length=100), nullable=False),
        sa.Column('waypoints', sa.JSON(), nullable=True),
        sa.Column('route_geojson', sa.JSON(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('planned_duration', sa.Integer(), nullable=True),
        sa.Column('total_distance', sa.Float(), nullable=True),
        sa.Column('estimated_budget', sa.Float(), nullable=True),
        sa.Column('actual_budget', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trips_user_id'), 'trips', ['user_id'], unique=False)

    # 创建POI表
    op.create_table('pois',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('province', sa.String(length=50), nullable=True),
        sa.Column('city', sa.String(length=50), nullable=True),
        sa.Column('district', sa.String(length=50), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('price_level', sa.String(length=20), nullable=True),
        sa.Column('business_hours', sa.JSON(), nullable=True),
        sa.Column('is_24h', sa.Boolean(), nullable=True),
        sa.Column('services', sa.JSON(), nullable=True),
        sa.Column('facilities', sa.JSON(), nullable=True),
        sa.Column('payment_methods', sa.JSON(), nullable=True),
        sa.Column('photos', sa.JSON(), nullable=True),
        sa.Column('videos', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('external_url', sa.String(length=500), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pois_name'), 'pois', ['name'], unique=False)
    op.create_index(op.f('ix_pois_category'), 'pois', ['category'], unique=False)
    op.create_index('idx_poi_location', 'pois', ['longitude', 'latitude'], unique=False)
    op.create_index('idx_poi_category_location', 'pois', ['category', 'longitude', 'latitude'], unique=False)

    # 创建记忆表
    op.create_table('memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('memory_type', sa.String(length=50), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('related_trip_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_poi_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('importance_score', sa.String(length=20), nullable=True),
        sa.Column('confidence_score', sa.String(length=20), nullable=True),
        sa.Column('access_count', sa.String(length=20), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.String(length=20), nullable=True),
        sa.Column('is_public', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memories_user_id'), 'memories', ['user_id'], unique=False)
    op.create_index(op.f('ix_memories_memory_type'), 'memories', ['memory_type'], unique=False)
    op.create_index('idx_memory_type_user', 'memories', ['memory_type', 'user_id'], unique=False)

    # 创建预警表
    op.create_table('alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('longitude', sa.String(length=50), nullable=True),
        sa.Column('latitude', sa.String(length=50), nullable=True),
        sa.Column('radius', sa.String(length=20), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('effective_duration', sa.String(length=50), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('related_trip_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_route_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('processed_by', sa.String(length=100), nullable=True),
        sa.Column('notified_users', sa.JSON(), nullable=True),
        sa.Column('notification_count', sa.String(length=20), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_alert_type'), 'alerts', ['alert_type'], unique=False)
    op.create_index(op.f('ix_alerts_severity'), 'alerts', ['severity'], unique=False)
    op.create_index('idx_alert_type_severity', 'alerts', ['alert_type', 'severity'], unique=False)
    op.create_index('idx_alert_location', 'alerts', ['longitude', 'latitude'], unique=False)
    op.create_index('idx_alert_time', 'alerts', ['start_time', 'end_time'], unique=False)

    # 创建路线表
    op.create_table('routes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_location', sa.String(length=100), nullable=False),
        sa.Column('end_location', sa.String(length=100), nullable=False),
        sa.Column('waypoints', sa.JSON(), nullable=True),
        sa.Column('total_distance', sa.Float(), nullable=True),
        sa.Column('total_duration', sa.Integer(), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('route_geojson', sa.JSON(), nullable=True),
        sa.Column('route_steps', sa.JSON(), nullable=True),
        sa.Column('route_polyline', sa.Text(), nullable=True),
        sa.Column('route_type', sa.String(length=50), nullable=True),
        sa.Column('difficulty_level', sa.String(length=20), nullable=True),
        sa.Column('scenic_rating', sa.String(length=20), nullable=True),
        sa.Column('road_types', sa.JSON(), nullable=True),
        sa.Column('highway_percentage', sa.Float(), nullable=True),
        sa.Column('toll_cost', sa.Float(), nullable=True),
        sa.Column('motorcycle_friendly', sa.Boolean(), nullable=True),
        sa.Column('avoid_highway', sa.Boolean(), nullable=True),
        sa.Column('off_road_segments', sa.JSON(), nullable=True),
        sa.Column('safety_score', sa.Float(), nullable=True),
        sa.Column('hazards', sa.JSON(), nullable=True),
        sa.Column('restrictions', sa.JSON(), nullable=True),
        sa.Column('gas_stations', sa.JSON(), nullable=True),
        sa.Column('repair_shops', sa.JSON(), nullable=True),
        sa.Column('accommodations', sa.JSON(), nullable=True),
        sa.Column('restaurants', sa.JSON(), nullable=True),
        sa.Column('attractions', sa.JSON(), nullable=True),
        sa.Column('scenic_spots', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_route_locations', 'routes', ['start_location', 'end_location'], unique=False)
    op.create_index('idx_route_type_difficulty', 'routes', ['route_type', 'difficulty_level'], unique=False)
    op.create_index('idx_route_motorcycle', 'routes', ['motorcycle_friendly', 'avoid_highway'], unique=False)


def downgrade() -> None:
    # 删除表
    op.drop_table('routes')
    op.drop_table('alerts')
    op.drop_table('memories')
    op.drop_table('pois')
    op.drop_table('trips')
    op.drop_table('user_preferences')
    op.drop_table('users')

