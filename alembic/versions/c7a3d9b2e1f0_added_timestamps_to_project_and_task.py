"""Added timestamps to project and task

Revision ID: c7a3d9b2e1f0
Revises: e4f8c2a9d1b0
Create Date: 2026-07-14 16:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c7a3d9b2e1f0'
down_revision: Union[str, Sequence[str], None] = 'e4f8c2a9d1b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('project', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('project', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('task', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('task', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    op.drop_column('task', 'updated_at')
    op.drop_column('task', 'created_at')
    op.drop_column('project', 'updated_at')
    op.drop_column('project', 'created_at')
