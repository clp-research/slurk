#!/bin/bash

# create a slurk room with TOKEN NAME and LABEL

TOKEN=$1
NAME=$2
LABEL=$3

if [ $# -eq 3 ]
then
  curl -X POST \
         -H "Authorization: Token $TOKEN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{\"name\": \"$NAME\", \"label\": \"$LABEL\"}" \
         localhost/api/v2/room
else
  echo "You need to supply a token, a room name and a label"
  echo "e.g. sh $0 \$ADMIN_TOKEN test_room 'Test Room'"
fi
