"""Remove unique constraint from journey_measurements

Revision ID: 80fc315ceec8
Revises: 19ce8a520020
Create Date: 2025-02-06 12:48:18.025784
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "80fc315ceec8"
down_revision = "19ce8a520020"
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Remove unique constraint from journey_measurements"""
    op.drop_constraint("uq_journey_measurement", "journey_measurements", type_="unique")


def downgrade() -> None:
    """Re-add the unique constraint if rolling back"""
    op.create_unique_constraint("uq_journey_measurement", "journey_measurements", ["journey_id", "transit_mode_id"])
