"""add velafi_api_log table

Revision ID: 20250819_velafi_api_log_table
Revises: 20240729_velafi_kyc
Create Date: 2025-08-19 12:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250819_velafi_api_log_table'
# depend on latest existing revision; adjust if different
revises = '20240729_velafi_kyc'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'velafi_api_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('method', sa.String(length=8), nullable=False),
        sa.Column('endpoint', sa.String(length=128), nullable=False),
        sa.Column('request_payload', sa.JSON(), nullable=True),
        sa.Column('response_payload', sa.JSON(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_velafi_api_log_endpoint', 'velafi_api_log', ['endpoint'])
    op.create_index('ix_velafi_api_log_created_at', 'velafi_api_log', ['created_at'])

def downgrade() -> None:
    op.drop_index('ix_velafi_api_log_created_at', table_name='velafi_api_log')
    op.drop_index('ix_velafi_api_log_endpoint', table_name='velafi_api_log')
    op.drop_table('velafi_api_log') 