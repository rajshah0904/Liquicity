#!/bin/bash
set -e

# Function to check if the database exists
database_exists() {
  psql -U postgres -lqt | cut -d \| -f 1 | grep -qw liquicity
}

# Function to create test users and initial data
create_test_data() {
  echo "Creating test users and initial data..."
  
  # Execute the Python script to create test users
  cd /workspace
  python create_test_user.py
  python create_second_test_user.py
  
  echo "Test users created successfully."
}

# Main execution starts here
echo "Initializing database..."

# Wait for PostgreSQL to start
until pg_isready -h localhost -U postgres; do
  echo "Waiting for PostgreSQL to start..."
  sleep 2
done

# Create database and user if they don't exist
if database_exists; then
  echo "Database 'liquicity' already exists."
else
  echo "Creating database 'liquicity'..."
  psql -U postgres -c "CREATE DATABASE liquicity;"
  psql -U postgres -c "CREATE USER raj WITH ENCRYPTED PASSWORD 'Rajshah11';"
  psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE liquicity TO raj;"
  
  # Run migrations
  cd /workspace
  echo "Running database migrations..."
  alembic upgrade head
  
  # Create test data
  create_test_data
fi

echo "Database initialization complete." 