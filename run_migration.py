import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection details
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://raj:Rajshah11@localhost:5432/liquicity")

def run_migration():
    """
    Run the SQL migration to remove blockchain and stablecoin-related fields
    from the database schema.
    """
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False  # We'll manage the transaction manually
        cursor = conn.cursor()

        print("Reading migration SQL file...")
        with open("database_migrations/remove_blockchain_fields.sql", "r") as f:
            migration_sql = f.read()

        print("Executing migration...")
        cursor.execute(migration_sql)
        
        print("Committing changes...")
        conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        if conn:
            conn.rollback()
            print("Changes rolled back due to error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Starting database migration to remove blockchain and AI-related fields...")
    run_migration()
    print("Migration process completed.") 