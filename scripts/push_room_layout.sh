#!/bin/bash

# tell the server what the room looks like

ADMIN=$1
ROOM_JSON=$2
ROOM_LAYOUT=$3

if [ "$#" -eq 3 ]
then
  export $ROOM_LAYOUT=$(curl -X POST \
         -H "Authorization: Token $ADMIN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d @$ROOM_JSON \
         localhost/api/v2/layout | jq .id)
else
  echo "You need to specify the authorization token, the room.json and a room environment variable name"
  echo "Ex: 'sh $0 \$ADMIN_TOKEN waiting_room_layout.json WAITING_ROOM_LAYOUT'"
fi
