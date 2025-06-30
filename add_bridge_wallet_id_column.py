import psycopg2
from clean_backend.database import DATABASE_URL


def add_bridge_wallet_id_column():
    """Add bridge_wallet_id column to the users_v2 table if it doesn't exist."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check if the column already exists
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='users_v2' AND column_name='bridge_wallet_id';
            """
        )
        if cursor.fetchone() is None:
            print("Adding bridge_wallet_id column to users_v2 table…")
            cursor.execute(
                """
                ALTER TABLE users_v2
                ADD COLUMN bridge_wallet_id VARCHAR(64) UNIQUE;
                """
            )
            conn.commit()
            print("bridge_wallet_id column added successfully!")
        else:
            print("bridge_wallet_id column already exists in users_v2 table.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error adding bridge_wallet_id column: {e}")
        return False

    return True


if __name__ == "__main__":
    add_bridge_wallet_id_column() 