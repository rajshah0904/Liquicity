"""Create VelaFi KYC tables

Revision ID: 20240729_velafi_kyc
Revises: 20240729_velafi_core
Create Date: 2024-07-29 12:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = '20240729_velafi_kyc'
down_revision = '20240729_velafi_core'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create velafi_customers table
    op.create_table('velafi_customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('velafi_customer_id', sa.String(length=64), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('date_of_birth', sa.String(length=10), nullable=False),
        sa.Column('country', sa.String(length=2), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('kyc_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('kyc_submitted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('kyc_verified_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('rejection_reasons', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users_v2.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create velafi_kyc_documents table
    op.create_table('velafi_kyc_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('velafi_customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('velafi_document_id', sa.String(length=64), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='uploaded'),
        sa.Column('uploaded_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('verified_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['velafi_customer_id'], ['velafi_customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_velafi_customers_user_id'), 'velafi_customers', ['user_id'], unique=True)
    op.create_index(op.f('ix_velafi_customers_velafi_customer_id'), 'velafi_customers', ['velafi_customer_id'], unique=True)
    op.create_index(op.f('ix_velafi_kyc_documents_velafi_customer_id'), 'velafi_kyc_documents', ['velafi_customer_id'], unique=False)
    op.create_index(op.f('ix_velafi_kyc_documents_velafi_document_id'), 'velafi_kyc_documents', ['velafi_document_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_velafi_kyc_documents_velafi_document_id'), table_name='velafi_kyc_documents')
    op.drop_index(op.f('ix_velafi_kyc_documents_velafi_customer_id'), table_name='velafi_kyc_documents')
    op.drop_index(op.f('ix_velafi_customers_velafi_customer_id'), table_name='velafi_customers')
    op.drop_index(op.f('ix_velafi_customers_user_id'), table_name='velafi_customers')
    
    # Drop tables
    op.drop_table('velafi_kyc_documents')
    op.drop_table('velafi_customers') 