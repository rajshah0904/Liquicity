#!/bin/bash
set -e

export PGPASSWORD=${POSTGRES_PASSWORD:-Rajshah11}

wait_for_postgres() {
  echo "Waiting for PostgreSQL to be ready..."
  until pg_isready -h ${POSTGRES_HOST:-db} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-raj} > /dev/null 2>&1; do
    sleep 1
  done
  echo "PostgreSQL is ready!"
}

if [ -n "$CODESPACES" ] || [ -n "$DEVCONTAINER" ]; then
  wait_for_postgres
fi

exec "$@"
