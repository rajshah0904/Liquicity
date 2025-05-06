#!/bin/bash
set -e

# Setup PostgreSQL
export PGPASSWORD=${POSTGRES_PASSWORD:-Rajshah11}

# Function to wait for PostgreSQL to be ready
wait_for_postgres() {
  echo "Waiting for PostgreSQL to be ready..."
  until pg_isready -h ${POSTGRES_HOST:-db} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-raj} > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL to be ready..."
    sleep 1
  done
  echo "PostgreSQL is ready!"
}

# If we're in a devcontainer, wait for PostgreSQL
if [ -n "$CODESPACES" ] || [ -n "$DEVCONTAINER" ]; then
  wait_for_postgres
fi

# Execute the provided command or default to sleep infinity
exec "$@" 