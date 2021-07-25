#!/usr/bin/env bash
set -eu

# Parameters:
#   scripts/create_room_token.sh room_id permissions_path [registrations_left] [task_id]
# Environment variables:
#   SLURK_TOKEN: Token to pass as authorization, defaults to `00000000-0000-0000-0000-000000000000`
#   SLURK_HOST: Host name to use for the request, defaults to `http://localhost`
#   SLURK_PORT: Port to use for the request, defaults to 5000

TOKEN=${SLURK_TOKEN:=00000000-0000-0000-0000-000000000000}
HOST=${SLURK_HOST:-http://localhost}
PORT=${SLURK_PORT:-5000}

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 room_id permissions_path [registrations_left] [task_id]" 1>&2
  echo "For more info see $HOST:$PORT/rapidoc#post-/slurk/api/tokens"
  exit 1
fi

ROOM=$1
REGISTRATIONS=${3:-1}
TASK=${4:-null}

permissions_path=$2

function check_error {
    if [ "$(jq '. | has("code")' <<< "$1")" = true ]; then
        jq -r .message <<< "$1" 1>&2
        if [ "$(jq '. | has("errors")' <<< "$1")" = true ]; then
            jq -r .errors <<< "$1" 1>&2
        fi
        exit 1
    fi
}

response=$(curl -sX POST $HOST:$PORT/slurk/api/permissions \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d @$permissions_path)
check_error "$response"
permissions=$(echo "$response" | jq .id)

response=$(curl -sX POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "{\"permissions_id\": $permissions, \"room_id\": $ROOM, \"registrations_left\": $REGISTRATIONS, \"task_id\": $TASK}" \
    $HOST:$PORT/slurk/api/tokens)
check_error "$response"
echo "$response" | jq
