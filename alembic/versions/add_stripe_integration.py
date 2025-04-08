"""Add Stripe integration

Revision ID: 20231215_01
Revises: 
Create Date: 2023-12-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20231215_01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add stripe_customer_id column to users table
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(), nullable=True))
    
    # Add first_name and last_name columns to users table if they don't exist
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
    
    # Create bank_accounts table
    op.create_table(
        'bank_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stripe_bank_id', sa.String(), nullable=False, index=True),
        sa.Column('bank_name', sa.String(), nullable=False),
        sa.Column('account_type', sa.String(), nullable=False),
        sa.Column('last4', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('last_updated', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on user_id
    op.create_index('ix_bank_accounts_user_id', 'bank_accounts', ['user_id'])
    
    # Create unique index on stripe_bank_id
    op.create_index('ix_bank_accounts_stripe_bank_id_unique', 'bank_accounts', ['stripe_bank_id'], unique=True)


def downgrade():
    # Drop bank_accounts table
    op.drop_table('bank_accounts')
    
    # Remove stripe_customer_id column from users table
    op.drop_column('users', 'stripe_customer_id')
    
    # Remove first_name and last_name columns from users table
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name') 