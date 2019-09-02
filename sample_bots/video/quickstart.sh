#!/usr/bin/env bash

docker kill video-server > /dev/null 2> /dev/null
docker rm video-server > /dev/null 2> /dev/null

docker kill concierge-bot > /dev/null 2> /dev/null
docker rm concierge-bot > /dev/null 2> /dev/null

docker build -t slurk/server -f docker/slurk/Dockerfile .

set -eux

SLURK_SERVER_ID=$(docker run -p 80:5000 --name video-server -e SECRET_KEY=your-key -d slurk/server)

sleep 1
ADMIN_TOKEN=$(docker logs "$SLURK_SERVER_ID" 2> /dev/null | sed -n '/admin token:/{n;p;}')

pushd sample_bots/concierge
WAITING_ROOM_LAYOUT=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d @layout.json \
       localhost/api/v2/layout | jq .id)

WAITING_ROOM=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d "{\"name\": \"waiting_room\", \"label\": \"Waiting Room\", \"layout\": $WAITING_ROOM_LAYOUT}" \
       localhost/api/v2/room | jq .name)
popd

pushd sample_bots/video
VIDEO_ROOM_LAYOUT=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d @layout.json \
       localhost/api/v2/layout | jq .id)
echo $VIDEO_ROOM_LAYOUT
popd

TASK_ID=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d "{\"name\": \"Video\", \"num_users\": 2, \"layout\": $VIDEO_ROOM_LAYOUT }" \
       localhost/api/v2/task | jq .id)

CONCIERGE_BOT_TOKEN=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d '{"room": "waiting_room", "message_text": true, "room_create": true, "user_room_join": true, "user_room_leave": true}' \
       localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/')
docker run -e TOKEN=$CONCIERGE_BOT_TOKEN --name concierge-bot --net="host" -d slurk/concierge-bot


VIDEO_BOT_TOKEN=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d '{"room": "waiting_room", "message_text": true, "message_command": true, "user_room_join": true}' \
       localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/')

CLIENT_TOKEN_1=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d "{\"room\": \"waiting_room\", \"task\": $TASK_ID, \"message_text\": true}" \
       localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/')
firefox "localhost/login/?next=%2F&name=client1&token=$CLIENT_TOKEN_1"

CLIENT_TOKEN_2=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d "{\"room\": \"waiting_room\", \"task\": $TASK_ID, \"message_text\": true}" \
       localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/')
echo $CLIENT_TOKEN_2
#firefox --private-window "localhost/login/?next=%2F&name=client2&token=$CLIENT_TOKEN_2"

#python sample_bots/video/video.py -t "$VIDEO_BOT_TOKEN" --task_id "$TASK_ID" --openvidu-secret-key "MY_SECRET"

docker logs -f "$SLURK_SERVER_ID"