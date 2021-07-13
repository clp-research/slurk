#!/usr/bin/env bash
set -eu

# Parameters:
#   scripts/create_room.sh layout_id [session_id]
# Environment variables:
#   SLURK_TOKEN: Token to pass as authorization, defaults to `00000000-0000-0000-0000-000000000000`
#   SLURK_HOST: Host name to use for the request, defaults to `http://localhost`
#   SLURK_PORT: Port to use for the request, defaults to 80

TOKEN=${SLURK_TOKEN:=00000000-0000-0000-0000-000000000000}
HOST=${SLURK_HOST:-http://localhost}
PORT=${SLURK_PORT:-5000}

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 layout_id [session_id]" 1>&2
  echo "For more info see $HOST:$PORT/rapidoc#post-/slurk/api/rooms"
  exit 1
fi

LAYOUT=$1
if [ -z ${2+x} ]; then
    SESSION=
else
    SESSION=", \"openvidu_session_id\": \"$2\""
fi

function check_error {
    if [ "$(jq '. | has("code")' <<< "$1")" = true ]; then
        jq -r .message <<< "$1" 1>&2
        if [ "$(jq '. | has("errors")' <<< "$1")" = true ]; then
            jq -r .errors <<< "$1" 1>&2
        fi
        exit 1
    fi
}

response=$(curl -sX POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "{\"layout_id\": $LAYOUT $SESSION}" \
    $HOST:$PORT/slurk/api/rooms)
check_error "$response"
echo "$response" | jq
