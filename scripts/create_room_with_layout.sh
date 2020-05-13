#!/bin/bash

# create a slurk room with TOKEN, NAME and LABEL, and LAYOUT
# TOKEN: typically the $ADMIN_TOKEN
# NAME: an identifier, typically in snake_case
# LABEL: a string name, must be enclosed in quotes if it contains whitespace
# LAYOUT: an id that was assigned by push_room_layout.sh, e.g. 2

TOKEN=$1
NAME=$2
LABEL=$3
LAYOUT=$4

if [ $# -eq 4 ]
then
  curl -X POST \
         -H "Authorization: Token $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{\"name\": \"$NAME\", \"label\": \"$LABEL\", \"layout\": $LAYOUT}" \
         localhost/api/v2/room
else
  echo "You need to supply a token, a room name and a label"
  echo "e.g. sh $0 \$ADMIN_TOKEN waiting_room 'Waiting Room' \$ROOM_LAYOUT"
fi
