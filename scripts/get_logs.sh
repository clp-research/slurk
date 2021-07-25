#!/usr/bin/env bash
set -eu

# Parameters:
#   scripts/print_logs.sh room_id
# Environment variables:
#   SLURK_TOKEN: Token to pass as authorization, defaults to `00000000-0000-0000-0000-000000000000`
#   SLURK_HOST: Host name to use for the request, defaults to `http://localhost`
#   SLURK_PORT: Port to use for the request, defaults to 5000

TOKEN=${SLURK_TOKEN:=00000000-0000-0000-0000-000000000000}
HOST=${SLURK_HOST:-http://localhost}
PORT=${SLURK_PORT:-5000}

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 room_id" 1>&2
  echo "For more info see $HOST:$PORT/rapidoc#get-/slurk/api/logs"
  exit 1
fi

ROOM=$1

response=$(curl -sX GET \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    $HOST:$PORT/slurk/api/logs?room_id=$ROOM)
echo "$response"
