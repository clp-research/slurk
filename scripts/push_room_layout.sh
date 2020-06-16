#!/bin/bash

# tell the server what the room looks like

ADMIN=$1
ROOM_JSON=$2

if [ "$#" -eq 2 ]
then
  curl -X POST \
         -H "Authorization: Token $ADMIN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d @$ROOM_JSON \
         localhost/api/v2/layout | jq .id
else
  echo "You need to specify the authorization token and the room.json"
  echo "Ex: 'sh $0 \$ADMIN_TOKEN waiting_room_layout.json'"
fi
