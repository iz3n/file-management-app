#!/bin/sh
set -e
echo "Checking migrations..."
# Generate revision from models if no migration files exist (container uses autogenerate, not repo migrations)
if ! find /app/alembic/versions -maxdepth 1 -name '*.py' -print 2>/dev/null | grep -q .; then
  echo "No migrations found; generating from models..."
  alembic revision --autogenerate -m "initial"
fi
echo "Applying migrations..."
alembic upgrade head
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
