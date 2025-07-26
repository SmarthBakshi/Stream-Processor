#!/bin/bash
set -e

# Default port
PORT=5000

# Find a free port if 5000 is busy
while lsof -i :$PORT &>/dev/null; do
  echo "Port $PORT in use, trying next..."
  PORT=$((PORT+1))
done

# Start MLflow (Poetry environment)
echo "Starting MLflow UI on port $PORT..."
poetry run mlflow ui --port $PORT --backend-store-uri file:./mlflow/mlruns --default-artifact-root ./\mlflow/mlartifacts
