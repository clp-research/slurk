#!/bin/bash

set -eu

export FLASK_APP=slurk
export FLASK_ENV=development
export SLURK_SECRET_KEY=$RANDOM
export SLURK_PORT=80
export DATABASE=$(pwd)/slurk.db
export SLURK_OPENVIDU_URL=https://localhost
export SLURK_OPENVIDU_PORT=4443
export SLURK_OPENVIDU_SECRET=MY_SECRET
export SLURK_OPENVIDU_VERIFY=no
export SLURK_DOCKER=slurky




function errcho {
    echo "$@" 1>&2
}

function start_openvidu {
    errcho -n 'Starting openvidu...'

    OPENVIDU_RECORDING_DIR=$(pwd)/recordings

    mkdir -p $OPENVIDU_RECORDING_DIR
    docker rm openvidu 2> /dev/null | true
    docker top openvidu 2> /dev/null 1>&2 || docker run -d \
        --name=openvidu \
        -p $SLURK_OPENVIDU_PORT:4443 \
        -e OPENVIDU_SECRET=$SLURK_OPENVIDU_SECRET \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$OPENVIDU_RECORDING_DIR:$OPENVIDU_RECORDING_DIR" \
        -e OPENVIDU_RECORDING=true \
        -e OPENVIDU_RECORDING_PATH=$OPENVIDU_RECORDING_DIR \
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
    errcho -n 'Starting slurk... '
    docker kill $SLURK_DOCKER 2> /dev/null | true
    docker rm $SLURK_DOCKER 2> /dev/null | true

    docker run -d \
        --name=$SLURK_DOCKER \
        --network host \
        -e FLASK_ENV=$FLASK_ENV \
        -e SLURK_SECRET_KEY=$SLURK_SECRET_KEY \
        -e SLURK_OPENVIDU_URL=$SLURK_OPENVIDU_URL \
        -e SLURK_OPENVIDU_PORT=$SLURK_OPENVIDU_PORT \
        -e SLURK_OPENVIDU_SECRET=$SLURK_OPENVIDU_SECRET \
        -e SLURK_OPENVIDU_VERIFY=$SLURK_OPENVIDU_VERIFY \
        -e PYTHONWARNINGS='ignore:Unverified HTTPS request' \
        -v "$DATABASE:/slurk.db" \
        -e SLURK_DATABASE_URI=sqlite:////slurk.db \
        slurk/server:dev > /dev/null
    errcho 'done'
}

rm slurk.db
touch slurk.db
start_openvidu
start_slurk
export SLURK_TOKEN=$(scripts/read_admin_token.sh)
LAYOUT=$(scripts/create_layout.sh slurk/views/static/layouts/default.json | jq -r .id)
SESSION=$(scripts/create_openvidu_session.sh | jq -r .id)
ROOM=$(scripts/create_room.sh $LAYOUT $SESSION | jq -r .id)
TOKEN=$(scripts/create_room_token.sh $ROOM -1 | jq -r .id)

brave "http://localhost:$SLURK_PORT/login/?next=%2F&name=Brave&token=$TOKEN" &
firefox "http://localhost:$SLURK_PORT/login/?next=%2F&name=Firefox&token=$TOKEN" &

docker logs slurky
docker attach slurky
