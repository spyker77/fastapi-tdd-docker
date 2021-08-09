#!/bin/sh

set -e

WEB_IMAGE_ID=$(docker inspect ${HEROKU_REGISTRY_WEB_IMAGE} --format={{.Id}})
WORKER_IMAGE_ID=$(docker inspect ${HEROKU_REGISTRY_WORKER_IMAGE} --format={{.Id}})
PAYLOAD='{"updates": [{"type": "web", "docker_image": "'"$WEB_IMAGE_ID"'"}, {"type": "worker", "docker_image": "'"$WORKER_IMAGE_ID"'"}]}'

curl -n -X PATCH https://api.heroku.com/apps/$HEROKU_APP_NAME/formation \
  -d "${PAYLOAD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3.docker-releases" \
  -H "Authorization: Bearer ${HEROKU_AUTH_TOKEN}"