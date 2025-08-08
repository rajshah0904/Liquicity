"""Add velafi_orders table and transfer_status enum

Revision ID: 20250807_velafi
Revises: 20240729_velafi_core
Create Date: 2025-08-07
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20250807_velafi"
down_revision = "20240729_velafi_core"
branch_labels = None
depends_on = None


# ---------------------------------------------------------------------------
# ENUM TYPES
# ---------------------------------------------------------------------------

velafi_direction_enum = postgresql.ENUM(
    "BUY",
    "SELL",
    name="velafi_direction",
)

velafi_status_enum = postgresql.ENUM(
    "pending",
    "processing",
    "completed",
    "failed",
    "partial",
    name="velafi_status",
)

transfer_status_enum = postgresql.ENUM(
    "PENDING",
    "COMPLETED",
    "FAILED",
    name="transfer_status",
)


def upgrade() -> None:
    # Create ENUMs
    velafi_direction_enum.create(op.get_bind(), checkfirst=True)
    velafi_status_enum.create(op.get_bind(), checkfirst=True)
    transfer_status_enum.create(op.get_bind(), checkfirst=True)

    # ---------------------------------------------------------------------
    # velafi_orders table
    # ---------------------------------------------------------------------
    op.create_table(
        "velafi_orders",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("direction", sa.Enum(name="velafi_direction"), nullable=False),
        sa.Column("fiat_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("fiat_currency", sa.String(length=3), nullable=False),
        sa.Column("usdc_amount", sa.Numeric(18, 2)),
        sa.Column("fx_rate", sa.Numeric(18, 6)),
        sa.Column("fee_usd", sa.Numeric(18, 2)),
        sa.Column("rail", sa.String(length=16)),
        sa.Column("status", sa.Enum(name="velafi_status"), nullable=False, server_default="pending"),
        sa.Column("tx_hash", sa.String(length=66)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_velafi_orders_order_id", "velafi_orders", ["order_id"], unique=True)
    op.create_index("ix_velafi_orders_user_id", "velafi_orders", ["user_id"], unique=False)

    # ---------------------------------------------------------------------
    # transfers table: add status column (enum) & indexes
    # ---------------------------------------------------------------------
    op.add_column("transfers", sa.Column("status", sa.Enum(name="transfer_status"), nullable=False, server_default="PENDING"))
    op.alter_column("transfers", "customer_id", existing_type=sa.String(length=50), index=True)
    op.alter_column("transfers", "user_id", existing_type=postgresql.UUID(as_uuid=True), index=True)


def downgrade() -> None:
    # Drop added column
    op.drop_column("transfers", "status")

    # Drop table & indexes
    op.drop_index("ix_velafi_orders_user_id", table_name="velafi_orders")
    op.drop_index("ix_velafi_orders_order_id", table_name="velafi_orders")
    op.drop_table("velafi_orders")

    # Drop ENUMs
    transfer_status_enum.drop(op.get_bind(), checkfirst=True)
    velafi_status_enum.drop(op.get_bind(), checkfirst=True)
    velafi_direction_enum.drop(op.get_bind(), checkfirst=True)
