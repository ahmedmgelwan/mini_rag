#!/bin/bash
set -e

echo "Running database migrations...."
cd /app/models/db_schemes/mini_rag/
alembic upgrade head
cd /app

# Start the app so the container keeps running
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 3