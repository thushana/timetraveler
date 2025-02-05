"""Modify journey measurement unique constraint

Revision ID: 19ce8a520020
Revises: 0a20d1ceb189
Create Date: 2025-02-05 05:38:47.905125
"""
from typing import Sequence, Union
from alembic import op

revision: str = '19ce8a520020'
down_revision: Union[str, None] = '0a20d1ceb189'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_constraint('uq_journey_measurement', 'journey_measurements', type_='unique')
    op.create_unique_constraint(
        'uq_journey_measurement',
        'journey_measurements',
        ['journey_id', 'transit_mode_id']
    )

def downgrade() -> None:
    op.drop_constraint('uq_journey_measurement', 'journey_measurements', type_='unique')
    op.create_unique_constraint(
        'uq_journey_measurement',
        'journey_measurements',
        ['journey_id', 'transit_mode_id', 'timestamp']
    )