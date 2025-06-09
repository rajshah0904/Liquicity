"""Add JSONB KYC columns to users

Revision ID: 20240507_01
Revises: 20240506_01
Create Date: 2024-05-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240507_01'
down_revision = '20240506_01'
branch_labels = None
depends_on = None


def upgrade():
    # Add JSONB KYC columns
    op.add_column('users', sa.Column('kyc_country', sa.String(length=2), nullable=True))
    op.add_column('users', sa.Column('kyc_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'))
    op.add_column('users', sa.Column('kyc_status', sa.String(length=20), nullable=False, server_default='pending'))
    op.add_column('users', sa.Column('kyc_submitted_at', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('users', sa.Column('kyc_verified_at', sa.TIMESTAMP(timezone=True), nullable=True))


def downgrade():
    # Remove JSONB KYC columns
    op.drop_column('users', 'kyc_verified_at')
    op.drop_column('users', 'kyc_submitted_at')
    op.drop_column('users', 'kyc_status')
    op.drop_column('users', 'kyc_data')
    op.drop_column('users', 'kyc_country') 