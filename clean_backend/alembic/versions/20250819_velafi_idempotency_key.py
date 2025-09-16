"""add velafi_idempotency_key table

Revision ID: 20250819_velafi_idempotency_key
Revises: 20250819_velafi_api_log_table
Create Date: 2025-08-19 12:10:00
"""
from alembic import op
import sqlalchemy as sa

revision = '20250819_velafi_idempotency_key'
revises = '20250819_velafi_api_log_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'velafi_idempotency_key',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('response_json', sa.JSON(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('key', name='uq_velafi_idempotency_key'),
    )
    op.create_index('ix_velafi_idemp_created_at', 'velafi_idempotency_key', ['created_at'])

def downgrade() -> None:
    op.drop_index('ix_velafi_idemp_created_at', table_name='velafi_idempotency_key')
    op.drop_table('velafi_idempotency_key') 