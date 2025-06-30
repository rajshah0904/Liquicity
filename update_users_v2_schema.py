import psycopg2
import os

from clean_backend.database import DATABASE_URL

# Columns we expect on users_v2 and their SQL definitions
EXPECTED_COLUMNS = {
    "bridge_wallet_id": "VARCHAR(64) UNIQUE",
    "tos_url": "TEXT",
    "tos_status": "VARCHAR(20) DEFAULT 'pending'",
    "signed_agreement_id": "TEXT",
    "kyc_url": "TEXT",
    "rejection_reasons": "TEXT",
    "requirements_due": "TEXT",
}


def ensure_columns():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            # Fetch existing columns
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users_v2';
                """
            )
            existing_cols = {row[0] for row in cur.fetchall()}

            added = 0
            for col, definition in EXPECTED_COLUMNS.items():
                if col not in existing_cols:
                    print(f"Adding missing column {col} ...")
                    cur.execute(f"ALTER TABLE users_v2 ADD COLUMN {col} {definition};")
                    added += 1
            if added:
                conn.commit()
                print(f"Added {added} column(s) successfully.")
            else:
                print("All expected columns already exist – no changes made.")
    finally:
        conn.close()


if __name__ == "__main__":
    ensure_columns() 