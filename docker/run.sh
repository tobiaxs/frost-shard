#!/bin/bash

set -exo pipefail

echo "Waiting for Postgres..."

while ! nc -z postgres 5432; do
	sleep 0.1
done

echo "Postgres started"

poetry run alembic upgrade head

if [[ -z ${DEVELOPMENT} ]]; then

	COMMAND=("$(which uvicorn)" "frost_shard.main:app" "--limit-max-requests=10000" "--timeout-keep-alive=2" "--workers" "1" "--host" "0.0.0.0" "--port" "${PORT:-8000}")

else

	COMMAND=("$(which uvicorn)" "frost_shard.main:app" "--reload" "--workers" "1" "--host" "0.0.0.0" "--port" "${PORT:-8000}")

fi

exec "${COMMAND[@]}"
