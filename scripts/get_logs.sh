#!/bin/bash

# examine the log files of a particular room

TOKEN=$1
ROOM=$2

if [ "$#" -eq 2 ]
then
  curl -X GET \
        -H "Authorization: Token $TOKEN" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        localhost/api/v2/room/$ROOM/logs
else
  echo "You need to specify the admin token and the room name (id)"
  echo "Ex: 'sh $0 \$ADMIN_TOKEN test_room'"
fi
