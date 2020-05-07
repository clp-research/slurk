#!/bin/bash

# create a token for ROOM, authenticating with the ADMIN token
# (``sed`` removes quotation from JSON-string)

ADMIN=$1
ROOM=$2

if [ "$#" -eq 2 ]
then
  curl -X POST \
         -H "Authorization: Token $ADMIN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{\"room\": \"$ROOM\", \"message_text\": true}" \
         localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/'
else
  echo "You need to specify the authorization token and a room identifier"
  echo "Ex: 'sh $0 \$ADMIN_TOKEN test_room'"
fi
