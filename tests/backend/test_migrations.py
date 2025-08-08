import os
from contextlib import contextmanager

import pytest  # type: ignore
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from alembic import command
from alembic.config import Config

POSTGRES_URL_ENV = "TEST_DATABASE_URL"


def _is_postgres(url: str) -> bool:
    return url.startswith("postgresql://") or url.startswith("postgresql+psycopg2://")


@contextmanager
def _alembic_cfg(db_url: str):
    cfg = Config()
    cfg.set_main_option("script_location", "clean_backend/alembic")
    cfg.set_main_option("sqlalchemy.url", db_url)
    yield cfg


@pytest.mark.order(1)
def test_upgrade_head_creates_velafi_orders_schema():
    db_url = os.getenv(POSTGRES_URL_ENV)
    if not db_url or not _is_postgres(db_url):
        pytest.skip(f"Set {POSTGRES_URL_ENV} to a Postgres URL to run migration tests")

    engine: Engine = create_engine(db_url, future=True)

    with _alembic_cfg(db_url) as cfg:
        # upgrade to latest
        command.upgrade(cfg, "head")

    insp = inspect(engine)

    # 1) Table exists
    assert "velafi_orders" in insp.get_table_names(), "velafi_orders table must exist after upgrade"

    # 2) Columns sanity
    cols = {c["name"]: c for c in insp.get_columns("velafi_orders")}
    for required in [
        "id",
        "order_id",
        "user_id",
        "direction",
        "fiat_amount",
        "fiat_currency",
        "status",
        "created_at",
        "updated_at",
    ]:
        assert required in cols, f"Missing column {required}"

    # 3) transfer.status enum presence
    transfer_cols = {c["name"]: c for c in insp.get_columns("transfers")}
    assert "status" in transfer_cols, "transfers.status must be added"

    # Optional: verify enum type name via raw query
    with engine.connect() as conn:
        res = conn.execute(text(
            """
            SELECT t.typname
            FROM pg_type t
            JOIN pg_attribute a ON a.atttypid = t.oid
            JOIN pg_class c ON a.attrelid = c.oid
            WHERE c.relname = 'transfers' AND a.attname = 'status'
            """
        )).scalar()
        assert res in {"transfer_status"}, f"Unexpected enum type for transfers.status: {res}"