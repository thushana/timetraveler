"""DATABASE TABLES - Add tables

Revision ID: 0a20d1ceb189
Revises: 88bdad858b50
Create Date: 2025-02-03 20:26:29.012877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0a20d1ceb189'
down_revision: Union[str, None] = '88bdad858b50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create lookup tables
    op.create_table(
        'transit_modes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('mode', sa.String(50), unique=True, nullable=False)
    )

    op.create_table(
        'route_statuses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('status', sa.String(50), unique=True, nullable=False)
    )

    op.create_table(
        'days_of_week',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('day', sa.String(50), unique=True, nullable=False)
    )

    op.create_table(
        'time_periods',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('period', sa.String(50), unique=True, nullable=False)
    )

    op.create_table(
        'time_slots',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('slot', sa.String(50), unique=True, nullable=False)
    )

   # Insert initial data into lookup tables
    op.bulk_insert(
        sa.table('transit_modes', sa.column('mode', sa.String)),
        [
            {'mode': 'driving'},
            {'mode': 'driving_routed'},
            {'mode': 'bicycling'},
            {'mode': 'walking'},
            {'mode': 'transit'}
        ]
    )

    op.bulk_insert(
        sa.table('route_statuses', sa.column('status', sa.String)),
        [
            {'status': 'active'},
            {'status': 'error'},
            {'status': 'disabled'}
        ]
    )

    op.bulk_insert(
        sa.table('days_of_week', sa.column('day', sa.String)),
        [
            {'day': 'Sunday'},
            {'day': 'Monday'},
            {'day': 'Tuesday'},
            {'day': 'Wednesday'},
            {'day': 'Thursday'},
            {'day': 'Friday'},
            {'day': 'Saturday'}
        ]
    )

    op.bulk_insert(
        sa.table('time_periods', sa.column('period', sa.String)),
        [
            {'period': 'overnight'},
            {'period': 'dawn'},
            {'period': 'morning'},
            {'period': 'afternoon'},
            {'period': 'evening'},
            {'period': 'night'}
        ]
    )

    time_slots = []
    periods = ['overnight', 'dawn', 'morning', 'afternoon', 'evening', 'night']
    for hour in range(24):
        for minute in [0, 15, 30, 45]:
            if hour < 4:
                period = 'overnight'
            elif hour < 8:
                period = 'dawn'
            elif hour < 12:
                period = 'morning'
            elif hour < 16:
                period = 'afternoon'
            elif hour < 20:
                period = 'evening'
            else:
                period = 'night'
            time_slots.append({'slot': f'{hour:02d}_{minute:02d}_{period}'})

    op.bulk_insert(
        sa.table('time_slots', sa.column('slot', sa.String)),
        time_slots
    )

    # Create routes table with enhanced geographic support
    op.create_table(
        'routes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('country', sa.String(100), nullable=False),
        sa.Column('timezone', sa.Text, nullable=False),
        sa.Column('status_id', sa.Integer, sa.ForeignKey('route_statuses.id'), nullable=False, server_default='1'),
        sa.Column('error_message', sa.Text),
        sa.Column('maps_url', sa.Text),
        sa.Column('raw_data', sa.dialects.postgresql.JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    # Create route_waypoints table
    op.create_table(
        'route_waypoints',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('route_id', sa.Integer, sa.ForeignKey('routes.id'), nullable=False),
        sa.Column('sequence_number', sa.SmallInteger, nullable=False),
        sa.Column('place_id', sa.String(255), nullable=False),
        sa.Column('plus_code', sa.String(20), nullable=False),
        sa.Column('formatted_address', sa.Text, nullable=False),
        sa.Column('latitude', sa.Numeric(9, 7), nullable=False),
        sa.Column('longitude', sa.Numeric(10, 7), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('route_id', 'sequence_number', name='uq_route_sequence'),
        sa.UniqueConstraint('route_id', 'place_id', name='uq_route_place')
    )

    # Create route_processing_history table
    op.create_table(
        'route_processing_history',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('route_id', sa.Integer, sa.ForeignKey('routes.id'), nullable=False),
        sa.Column('processor_version', sa.String(50)),
        sa.Column('success', sa.Boolean, nullable=False),
        sa.Column('error_message', sa.Text),
        sa.Column('processing_time_ms', sa.Integer),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False)
    )

    # Create mileage_rates table
    op.create_table(
        'mileage_rates',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('rate_cents', sa.Integer, nullable=False),
        sa.Column('effective_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('effective_date', name='uq_effective_date')
    )

    # Create route_measurements table
    op.create_table(
        'route_measurements',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('route_id', sa.Integer, sa.ForeignKey('routes.id'), nullable=False),
        sa.Column('transit_mode_id', sa.Integer, sa.ForeignKey('transit_modes.id'), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('local_timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('day_of_week_id', sa.Integer, sa.ForeignKey('days_of_week.id'), nullable=False),
        sa.Column('time_slot_id', sa.Integer, sa.ForeignKey('time_slots.id'), nullable=False),
        sa.Column('duration_seconds', sa.Integer, nullable=False),
        sa.Column('distance_meters', sa.Numeric(10, 2), nullable=False),
        sa.Column('speed_kph', sa.Numeric(5, 2), nullable=False),
        sa.Column('raw_response', sa.dialects.postgresql.JSONB),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('route_id', 'transit_mode_id', 'timestamp', name='uq_route_measurement')
    )

    # Create route_legs table
    op.create_table(
        'route_legs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('route_measurement_id', sa.Integer, sa.ForeignKey('route_measurements.id'), nullable=False),
        sa.Column('sequence_number', sa.SmallInteger, nullable=False),
        sa.Column('start_waypoint_id', sa.Integer, sa.ForeignKey('route_waypoints.id'), nullable=False),
        sa.Column('end_waypoint_id', sa.Integer, sa.ForeignKey('route_waypoints.id'), nullable=False),
        sa.Column('duration_seconds', sa.Integer, nullable=False),
        sa.Column('distance_meters', sa.Numeric(10, 2), nullable=False),
        sa.Column('speed_kph', sa.Numeric(5, 2), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('route_measurement_id', 'sequence_number', name='uq_route_leg')
    )

    # Create route_time_slice_stats table
    op.create_table(
        'route_time_slice_stats',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('route_id', sa.Integer, sa.ForeignKey('routes.id'), nullable=False),
        sa.Column('transit_mode_id', sa.Integer, sa.ForeignKey('transit_modes.id'), nullable=False),
        sa.Column('day_of_week_id', sa.Integer, sa.ForeignKey('days_of_week.id'), nullable=False),
        sa.Column('time_slot_id', sa.Integer, sa.ForeignKey('time_slots.id'), nullable=False),
        sa.Column('analysis_period', sa.Integer, nullable=False),
        sa.Column('sample_start_date', sa.Date, nullable=False),
        sa.Column('sample_end_date', sa.Date, nullable=False),
        sa.Column('sample_count', sa.Integer, nullable=False),
        sa.Column('avg_duration_seconds', sa.Integer, nullable=False),
        sa.Column('min_duration_seconds', sa.Integer, nullable=False),
        sa.Column('max_duration_seconds', sa.Integer, nullable=False),
        sa.Column('std_dev_duration', sa.Numeric(10, 2), nullable=False),
        sa.Column('p50_duration_seconds', sa.Integer, nullable=False),
        sa.Column('p75_duration_seconds', sa.Integer, nullable=False),
        sa.Column('p90_duration_seconds', sa.Integer, nullable=False),
        sa.Column('p95_duration_seconds', sa.Integer, nullable=False),
        sa.Column('avg_speed_kph', sa.Numeric(5, 2), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('route_id', 'transit_mode_id', 'day_of_week_id', 'time_slot_id', 'analysis_period', name='uq_route_time_slice_stats')
    )

 
def downgrade():
    op.drop_table('route_time_slice_stats')
    op.drop_table('route_legs')
    op.drop_table('route_measurements')
    op.drop_table('mileage_rates')
    op.drop_table('route_processing_history')
    op.drop_table('route_waypoints')
    op.drop_table('routes')
    op.drop_table('time_slots')
    op.drop_table('time_periods')
    op.drop_table('days_of_week')
    op.drop_table('route_statuses')
    op.drop_table('transit_modes')
