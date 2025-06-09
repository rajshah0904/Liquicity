import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use hardcoded database URL since environment variable is not set
database_url = "postgresql://raj:Rajshah11@localhost:5432/liquicity"
print(f"Using database URL: {database_url}")

# Create engine and session
try:
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Query all users
    result = session.execute(text("SELECT id, username, email FROM users"))
    
    print("\nList of users in the database:")
    for row in result:
        print(f"ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")
    
    session.close()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 