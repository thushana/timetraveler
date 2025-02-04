"""Create initial tables for Timetraveler

Revision ID: 88bdad858b50
Revises: 
Create Date: 2025-02-03 16:45:17.434520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88bdad858b50'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
