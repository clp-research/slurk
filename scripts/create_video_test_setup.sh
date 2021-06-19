#!/usr/bin/env bash
set -eu

# define vars
PORT=5000
DATABASE=$(pwd)/slurk.db
DEBUG=true
OPENVIDU_URL=${OPENVIDU_URL:-'https://localhost'}
OPENVIDU_PORT=${OPENVIDU_PORT:-4443}
OPENVIDU_SECRET=${OPENVIDU_SECRET:-MY_SECRET}

function errcho {
    echo "$@" 1>&2
}

function check_command {
    if ! command -v $1 &> /dev/null; then
        errcho "\`$1\` could not be found"
        exit 2
    fi
}

function shutdown {
    errcho -n 'Shutting down slurk... '
    docker stop -t 10 slurky 2> /dev/null | true
    local stdout=$(docker logs slurky 2> /dev/null)
    local stderr=$(docker logs slurky 2>&1 >/dev/null)
    docker rm slurky 2> /dev/null | true
    errcho 'done'
    [ -z "$stdout" ] || >&2 printf "\nstdout:\n$stdout\n"
    [ -z "$stderr" ] || >&2 printf "\nstderr:\n$stderr\n"

    # errcho -n 'Shutting down openvidu... '
    # docker stop -t 10 openvidu 2> /dev/null | true
    # docker rm openvidu 2> /dev/null | true
    # errcho 'done'
    exit 1
}

function reset_database {
    local DATABASE=$1
    errcho -n 'Resetting database... '
    rm -f $DATABASE
    touch $DATABASE
    errcho 'done'
}

function build_docker {
    errcho 'Building docker image... '
    docker build -t slurk/server_local -f docker/slurk/Dockerfile_local .
}

function start_openvidu {
    if [ $OPENVIDU_URL != 'https://localhost' ]; then
        errcho "Using OpenVidu Server at $OPENVIDU_URL"
        return 0
    fi

    errcho -n 'Starting openvidu...'

    docker rm openvidu 2> /dev/null | true
    docker top openvidu 2> /dev/null 1>&2 || docker run -d \
        --name=openvidu \
        -p $OPENVIDU_PORT:4443 \
        -e OPENVIDU_SECRET=$OPENVIDU_SECRET \
        openvidu/openvidu-server-kms:2.18.0 > /dev/null

    for i in {1..600}; do
        local logs=$(docker logs openvidu 2>&1)
        if echo $logs | grep -q 'OpenVidu is ready'; then
            errcho " done"
            return 0
        fi
        sleep 1
        errcho -n .
        if [ $(($i % 20)) = 0 ]; then
            errcho
        fi
    done

    errcho " timed out!"
    return 1
}

function start_slurk {
    local DATABASE=$1
    local OPENVIDU_URL=$2
    local OPENVIDU_PORT=$3
    local OPENVIDU_SECRET=$4

    errcho -n 'Starting slurk... '
    docker kill slurky 2> /dev/null | true
    docker rm slurky 2> /dev/null | true

    docker run -d \
        --name=slurky \
        --network host \
        -e DEBUG=$DEBUG \
        -e SECRET_KEY=$RANDOM \
        -e OPENVIDU_URL=$OPENVIDU_URL \
        -e OPENVIDU_PORT=$OPENVIDU_PORT \
        -e OPENVIDU_SECRET=$OPENVIDU_SECRET \
        -e OPENVIDU_VERIFY=no \
        -e PYTHONWARNINGS='ignore:Unverified HTTPS request' \
        -v "$(pwd):/app:ro" \
        -v "$DATABASE:/slurk.db" \
        -e DATABASE=sqlite:////slurk.db \
        slurk/server_local > /dev/null
    errcho 'done'
}

function wait_for_admin_token {
    errcho -n "Waiting for admin token..."
    for i in {1..60}; do
        local logs=$(docker logs slurky 2>&1)
        if echo $logs | grep -q 'admin token'; then
            ADMIN_TOKEN=$(echo "$logs" | sed -n '/admin token/{n;p;}')
            break
        fi
        if echo $logs | grep -q ERROR; then
            errcho " failed!"
            shutdown
        fi
        sleep 1
        errcho -n .
    done

    if [ -z ${ADMIN_TOKEN+x} ]; then
        errcho " timed out!"
        shutdown
    fi

    errcho " done"
    echo "$ADMIN_TOKEN"
}

function check_error {
    if [ "$(jq '. | has("code")' <<< "$1")" = true ]; then
        errcho "failed!"
        jq -r .message <<< "$1" 1>&2
        if [ "$(jq '. | has("errors")' <<< "$1")" = true ]; then
            errcho "Errors:"
            jq -r .errors <<< "$1" 1>&2
        fi
        shutdown
    fi
}

function create_layout {
    local TOKEN=$1
    errcho -n 'Creating video room layout... '

    local json='{
        "title": "Video Room",
        "subtitle": "Test room for audio and video functionality",
        "show_latency": false,
        "scripts": {
            "incoming-text": ["display-text"],
            "incoming-image": ["display-image"],
            "submit-message": ["send-message"],
            "print-history": ["plain-history"]
        },
        "video_resolution": "320x240",
        "video_framerate": 60,
        "start_with_audio": false
    }'

    local response=$(curl -sX POST \
         -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "$(jq . <<< "$json")" \
         localhost:$PORT/slurk/api/layouts)
    check_error "$response"

    jq -r .id <<< "$response"

    errcho 'done'
}

function create_session {
    local TOKEN=$1

    errcho -n "Creating OpenVidu session... "

    local response=$(curl -sX POST \
         -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{}" \
         localhost:$PORT/slurk/api/openvidu/sessions)
    check_error "$response"

    jq -r .id <<< "$response"

    errcho 'done'
}

function create_room {
    local TOKEN=$1
    local LAYOUT=$2
    local SESSION=$3

    errcho -n "Creating video room with layout $LAYOUT... "

    local NAME='video_room'
    local LABEL='Video Room'

    local response=$(curl -sX POST \
         -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{\"layout_id\": $LAYOUT, \"openvidu_session_id\": \"$SESSION\"}" \
         localhost:$PORT/slurk/api/rooms)
    check_error "$response"

    jq -r .id <<< "$response"

    errcho 'done'
}

function create_permissions {
    local TOKEN=$1
    errcho -n 'Creating permissions... '

    local response=$(curl -sX POST \
         -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{\"send_message\": true, \"openvidu_role\": \"MODERATOR\"}" \
         localhost:$PORT/slurk/api/permissions)
    check_error "$response"

    errcho 'done'
    echo "$response" | jq -r .id
}

function create_token {
    local TOKEN=$1
    local PERMISSIONS=$2
    local ROOM=$3
    errcho -n "Creating token for room $ROOM... "

    local response=$(curl -sX POST \
         -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{\"room_id\": $ROOM, \"permissions_id\": $PERMISSIONS}" \
         localhost:$PORT/slurk/api/tokens)
    check_error "$response"

    errcho 'done'
    echo "$response" | jq -r .id
}

check_command docker
check_command curl
check_command jq

reset_database $DATABASE
build_docker
start_openvidu
start_slurk $DATABASE $OPENVIDU_URL $OPENVIDU_PORT $OPENVIDU_SECRET
ADMIN_TOKEN=$(wait_for_admin_token)
errcho "Admin token: $ADMIN_TOKEN"
LAYOUT_ID=$(create_layout $ADMIN_TOKEN)
SESSION_ID=$(create_session $ADMIN_TOKEN)
ROOM=$(create_room $ADMIN_TOKEN $LAYOUT_ID $SESSION_ID)
PERMISSIONS=$(create_permissions $ADMIN_TOKEN)
TOKEN_1=$(create_token $ADMIN_TOKEN $PERMISSIONS $ROOM)
errcho "$TOKEN_1"
TOKEN_2=$(create_token $ADMIN_TOKEN $PERMISSIONS $ROOM)
errcho "$TOKEN_2"

brave "http://localhost:$PORT/login/?next=%2F&name=Brave&token=$TOKEN_1" &
firefox "http://localhost:$PORT/login/?next=%2F&name=Firefox&token=$TOKEN_2" &

docker container attach slurky
