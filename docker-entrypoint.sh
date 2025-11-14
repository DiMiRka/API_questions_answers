#!/bin/bash

set -e

echo "Waiting for database to be ready..."

while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is ready!"

echo "Checking if database exists..."
if ! PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -lqt | cut -d \| -f 1 | grep -qw $POSTGRES_DB; then
  echo "Database $POSTGRES_DB does not exist, creating..."
  PGPASSWORD=$POSTGRES_PASSWORD createdb -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER $POSTGRES_DB
  echo "Database $POSTGRES_DB created successfully"
else
  echo "Database $POSTGRES_DB already exists"
fi

echo "Running database migrations..."
python -m alembic upgrade head

if [ $? -ne 0 ]; then
  echo "Migration failed!"
  exit 1
fi

echo "Migrations completed successfully!"

echo "Starting application..."
exec "$@"