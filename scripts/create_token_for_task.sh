#!/bin/bash

# create a token for ROOM and TASK, authenticating with the ADMIN token
# (``sed`` removes quotation from JSON-string)

ADMIN=$1
ROOM=$2
TASK=$3

if [ "$#" -eq 3 ]
then
  curl -X POST \
        -H "Authorization: Token $ADMIN" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "{\"room\": \"$ROOM\", \"message_text\": true, \"task\": $TASK}" \
        localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/'
else
  echo "You need to specify the authorization token, a room identifier and a task identifier"
  echo "Ex: 'sh $0 \$ADMIN_TOKEN test_room \$TASK_ID'"
fi
