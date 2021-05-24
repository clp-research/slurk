#!/usr/bin/env bash
set -eu

# define vars
PORT=80
DATABASE=$(pwd)/slurk.db
DEBUG=true

# reset database
rm -f $DATABASE
touch $DATABASE

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
    errcho -n 'Shutting down server... '
    docker stop -t 10 slurky 2> /dev/null | true
    local stdout=$(docker logs slurky 2> /dev/null)
    local stderr=$(docker logs slurky 2>&1 >/dev/null)
    docker rm slurky 2> /dev/null | true
    errcho 'done'
    [ -z "$stdout" ] || >&2 printf "\nstdout:\n$stdout\n"
    [ -z "$stderr" ] || >&2 printf "\nstderr:\n$stderr\n"
    exit 1
}

function build_docker {
    errcho 'Building docker image... '
    docker build -t slurk/server -f docker/slurk/Dockerfile .
    errcho 'done'
}

function start_server {
    errcho -n 'Starting server... '
    docker kill slurky 2> /dev/null | true
    docker rm slurky 2> /dev/null | true

    SLURK_SERVER_ID=$(docker run --name=slurky -p $PORT:5000 -e DEBUG=$DEBUG -e SECRET_KEY=$RANDOM -v $DATABASE:/slurk.db -e DATABASE=sqlite:////slurk.db -d slurk/server)
    errcho 'done'
}

function wait_for_admin_token {
    errcho -n "Waiting for admin token..."
    for i in {1..60}; do
        local logs=$(docker logs slurky 2>&1)
        if echo $logs | grep -q admin; then
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
    if [ "$(jq '. | has("error")' <<< "$1")" = true ]; then
        errcho "failed!"
        jq -r .error <<< "$1" 1>&2
        shutdown
    fi
}

function create_layout {
    local TOKEN=$1
    errcho -n 'Creating video room layout... '

    local json='{
        "title": "Video Room",
        "subtitle": "Test room for audio and video functionality",
        "scripts": {
            "incoming-text": "display-text",
            "incoming-image": "display-image",
            "submit-message": "send-message",
            "print-history": "plain-history"
        }
    }'

    local response=$(curl -sX POST \
         -H "Authorization: Token $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "$(jq . <<< "$json")" \
         localhost:$PORT/api/v2/layout)
    check_error "$response"

    jq -r .id <<< "$response"

    errcho 'done'
}

function create_room {
    local TOKEN=$1
    local LAYOUT=$2

    errcho -n 'Creating video room... '

    local NAME='video_room'
    local LABEL='Video Room'

    local response=$(curl -sX POST \
         -H "Authorization: Token $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{\"name\": \"$NAME\", \"label\": \"$LABEL\", \"layout\": $LAYOUT}" \
         localhost:$PORT/api/v2/room)
    check_error "$response"

    jq -r .name <<< "$response"

    errcho 'done'
}

function create_token {
    local TOKEN=$1
    local ROOM=$2
    errcho -n 'Creating token... '

    local response=$(curl -sX POST \
         -H "Authorization: Token $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{\"room\": \"$ROOM\", \"message_text\": true}" \
         localhost:$PORT/api/v2/token)
    check_error "$response"

    errcho 'done'
    echo "$response" | jq -r .id
}

check_command docker
check_command curl
check_command jq

build_docker
start_server
ADMIN_TOKEN=$(wait_for_admin_token)
LAYOUT_ID=$(create_layout $ADMIN_TOKEN)
ROOM=$(create_room $ADMIN_TOKEN $LAYOUT_ID)
TOKEN_1=$(create_token $ADMIN_TOKEN $ROOM)
errcho "$TOKEN_1"
TOKEN_2=$(create_token $ADMIN_TOKEN $ROOM)
errcho "$TOKEN_2"

#brave "http://localhost/login/?next=%2F&name=TOKEN1&token=$TOKEN_1"
#firefox "http://localhost/login/?next=%2F&name=TOKEN2&token=$TOKEN_2"
