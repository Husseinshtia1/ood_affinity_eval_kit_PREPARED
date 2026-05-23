#!/usr/bin/env sh
set -eu

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE="${1:-env.production.example}"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Missing $COMPOSE_FILE"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing env file: $ENV_FILE"
  exit 1
fi

echo "Validating Docker Compose configuration..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config >/tmp/prepared-compose-config.yml

echo "Docker Compose configuration is valid."
echo "Rendered config: /tmp/prepared-compose-config.yml"
echo ""
echo "Next manual checks after startup:"
echo "  docker compose -f $COMPOSE_FILE --env-file $ENV_FILE ps"
echo "  curl http://localhost:8000/health"
echo "  docker compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f api"
echo "  docker compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f worker"
