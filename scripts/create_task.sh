#!/bin/bash

# create a TASK_ID

ADMIN=$1
TASK_NAME=$2
USERS=$3

if [ "$#" -eq 3 ]
then
  export TASK_ID=$(curl -X POST \
         -H "Authorization: Token $ADMIN" \
         -H "Content-Type: application/json" \
         -H "Accept: application/json" \
         -d "{\"name\": \"$TASK_NAME\", \"num_users\": $USERS}" \
         localhost/api/v2/task | jq .id)
else
  echo "You need to specify the authorization token, a task name, and the number of users"
  echo "Ex: 'sh $0 \$ADMIN_TOKEN \"Echo Task\" 2'"
fi
