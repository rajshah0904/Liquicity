"""VelaFi core tables (payment methods + orders).

Revision ID: 20240729_velafi_core
Revises: 20240507_add_kyc_jsonb
Create Date: 2024-07-29
"""
from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20240729_velafi_core"
down_revision = "20240507_01"
branch_labels = None
depends_on = None

enum_name = "velafi_order_status"

def upgrade() -> None:
    # 1. Enum type
    order_status = sa.Enum("pending", "processing", "completed", "failed", name=enum_name)
    order_status.create(op.get_bind(), checkfirst=True)

    # 2. velafi_payment_methods
    op.create_table(
        "velafi_payment_methods",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", psql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("payment_method_id", sa.String, nullable=False, unique=True),
        sa.Column("plaid_token_hash", sa.String(64)),
        sa.Column("fiat_rail", sa.String(16)),
        sa.Column("country", sa.String(2)),
        sa.Column("currency", sa.String(3)),
        sa.Column("raw_payload", psql.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    # 3. velafi_orders
    op.create_table(
        "velafi_orders",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", psql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("payment_method_db_id", psql.UUID(as_uuid=True), sa.ForeignKey("velafi_payment_methods.id")),
        sa.Column("velafi_order_id", sa.String, nullable=False),
        sa.Column("fiat_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("fiat_currency", sa.String(3), default="USD"),
        sa.Column("status", sa.Enum(name=enum_name), nullable=False, server_default="pending"),
        sa.Column("usdc_amount", sa.Numeric(20, 6)),
        sa.Column("quote_rate", sa.Numeric(20, 8)),
        sa.Column("fee_usd", sa.Numeric(20, 2)),
        sa.Column("raw_payload", psql.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("velafi_order_id", name="uq_velafi_order_id"),
    )

    # indices created via column index True above are handled automatically by Alembic only in SQLAlchemy 2;
    # ensure explicit index for user_id on orders
    op.create_index("ix_velafi_orders_user", "velafi_orders", ["user_id"])

def downgrade() -> None:
    op.drop_index("ix_velafi_orders_user", table_name="velafi_orders")
    op.drop_table("velafi_orders")
    op.drop_table("velafi_payment_methods")
    sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True) 