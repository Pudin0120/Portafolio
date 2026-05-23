#!/bin/sh
set -e

echo "[entrypoint] Starting container entrypoint..."

# Bootstrap database safely for new and existing environments
echo "[entrypoint] Running database bootstrap (safe migrations)..."
python /app/scripts/bootstrap_db.py
echo "[entrypoint] OK Database bootstrap completed successfully"

# Run seed script conditionally
if [ "${RUN_SEED}" = "1" ] || [ "${RUN_SEED}" = "true" ] || [ "${RUN_SEED}" = "True" ]; then
	echo "[entrypoint] RUN_SEED is enabled - executing seed.py"
	# Run seed; don't abort container if seed fails but print error
	if ! python /app/seed.py; then
		echo "[entrypoint] Warning: seed.py returned a non-zero exit code. Continuing startup."
	fi
else
	echo "[entrypoint] RUN_SEED is disabled - skipping seed.py"
fi

# If arguments are passed to the container, execute them
if [ $# -gt 0 ]; then
	echo "[entrypoint] Executing command: $@"
	exec "$@"
fi

echo "[entrypoint] Starting application (uvicorn)..."
if [ "$ENVIRONMENT" = 'development' ]; then
	exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app
else
	exec uvicorn main:app --host 0.0.0.0 --port 8000
fi
