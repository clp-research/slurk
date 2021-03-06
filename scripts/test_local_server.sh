#!/bin/bash
set -eux

# define vars
PORT=5000
HOST=localhost
ADMIN_TOKEN=00000000-0000-0000-0000-000000000000

# stop running containers
#sudo docker kill slurky
#sudo docker rm slurky

# start docker container for slurk server
#SLURK_SERVER_ID=$(docker run --name=slurky -p $PORT:5000 -e SECRET_KEY=your-key -d slurk/server)
sleep 1

# create a room
curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d '{"name": "test_room", "label": "Test Room"}' \
       localhost:$PORT/api/v2/room
sleep 1

# generate a new token (can be used for mutliple clients for testing)
CLIENT_TOKEN=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d '{"room": "test_room", "message_text": true}' \
       localhost:$PORT/api/v2/token | sed 's/^"\(.*\)"$/\1/')

CLIENT_TOKEN_2=$(curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d '{"room": "test_room", "message_text": true}' \
       localhost:$PORT/api/v2/token | sed 's/^"\(.*\)"$/\1/')

# with CLIENT_TOKEN, launch the web app at localhost, port 5000 and fill in
# a custom user name and the client token
# for testing, open a second browser and login with different username but same token
