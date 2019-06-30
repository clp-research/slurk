ADMIN_TOKEN=00000000-0000-0000-0000-000000000000

WAITING_ROOM_LAYOUT=$(curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d "@sample_bots/concierge/layout.json" \
          localhost:5000/api/v2/layout | jq .id)

curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d "{\"name\": \"waiting_room\", \"label\": \"Waiting Room\", \"layout\": $WAITING_ROOM_LAYOUT}" \
          localhost:5000/api/v2/room

TASK_ID=$(curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d '{"name": "Echo Task", "num_users": 2}' \
          localhost:5000/api/v2/task | jq .id)

curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d "{\"room\": \"waiting_room\", \"message_text\": true, \"task\": $TASK_ID}" \
          localhost:5000/api/v2/token | sed 's/^"\(.*\)"$/\1/'

curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d "{\"room\": \"waiting_room\", \"message_text\": true, \"task\": $TASK_ID}" \
          localhost:5000/api/v2/token | sed 's/^"\(.*\)"$/\1/'

ECHO_BOT_TOKEN=$(curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d '{"room": "waiting_room", "message_text": true, "room_create": true, "user_room_join": true}' \
          localhost:5000/api/v2/token | sed 's/^"\(.*\)"$/\1/')

CONCIERGE_BOT_TOKEN=$(curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d '{"room": "waiting_room", "message_text": true, "room_create": true, "user_room_join": true}' \
          localhost:5000/api/v2/token | sed 's/^"\(.*\)"$/\1/')

docker run -e TOKEN=${ECHO_BOT_TOKEN} --net="host" -e CHAT_PORT=5000 -e ECHO_TASK_ID=${TASK_ID} -d slurk/echo-bot
docker run -e TOKEN=${CONCIERGE_BOT_TOKEN} --net="host" -e CHAT_PORT=5000 slurk/concierge-bot

docker stop -t 0 $(docker ps -aq) > /dev/null