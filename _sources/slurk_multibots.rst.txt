.. _slurk_multibots:

Pairing up participants and running multiple rooms
==================================================

In the following steps you will learn how to let bots and human users enter the slurk waiting room where users will be
paired up and put into a new task-specific chatroom along with bots. We provided an example bot handling this mechanism:
The **concierge bot** moves human users and other bots from the waiting room to a taskroom.

First of all, we need a waiting room and a task. For the waiting room, we submit the layout. Let's take the layout
provided in the *sample_bots* directory: ::

   $ curl https://raw.githubusercontent.com/clp-research/slurk/master/sample_bots/concierge/layout.json > waiting_room_layout.json

This layout now has to be pushed to the server. For this command you may have to install ``jq``: ::

   $ sudo apt-get install jq
   $ WAITING_ROOM_LAYOUT=$(curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d @waiting_room_layout.json \
          localhost/api/v2/layout | jq .id)

Ensure we have a valid id: ::

   $ echo $WAITING_ROOM_LAYOUT
   2

We can now create the waiting room with the associated layout: ::

   $ curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d "{\"name\": \"waiting_room\", \"label\": \"Waiting Room\", \"layout\": $WAITING_ROOM_LAYOUT}" \
          localhost/api/v2/room
   {
     "current_users": {},
     "label": "Waiting Room",
     "layout": null,
     "name": "waiting_room",
     "read_only": false,
     "show_latency": true,
     "show_users": true,
     "static": false,
     "users": {}
   }

The next step is to create a task. Each task contains information about the number of user required in order to start
the task: ::

   $ TASK_ID=$(curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d '{"name": "Echo Task", "num_users": 2}' \
          localhost/api/v2/task | jq .id)

The token for the bot is stored in ``CONCIERGE_BOT_TOKEN``: ::

   $ CONCIERGE_BOT_TOKEN=$(curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d '{"room": "waiting_room", "message_text": true, "room_create": true, "user_room_join": true, "user_room_leave": true}' \
          localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/')

Now start the concierge bot: ::

   $ docker run -e TOKEN=$CONCIERGE_BOT_TOKEN --net="host" slurk/concierge-bot


The concierge bot is joining the waiting room now. It waits for two users to join the waiting room, which has both the
specified task assigned. Once, both has joined, the bot will create a new task room and moves both users into that room.
We want the echo-bot to join this task room as well. The concierge bot emits two events, when creating a new task room:
``new_room`` and ``new_task_room``. The echo bot is able to listen to those events. So let's create a token for this
bot, too: ::


   $ ECHO_BOT_TOKEN=$(curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d '{"room": "waiting_room", "message_text": true, "user_room_join": true}' \
          localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/')

This bot has an optional ``task-id`` parameter, to listen to specific tasks to join. Let's start it: ::

   $ docker run -e TOKEN=$ECHO_BOT_TOKEN -e ECHO_TASK_ID=$TASK_ID --net="host" slurk/echo-bot

Now lets create two user tokens and specify the task: ::

   $ curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d "{\"room\": \"waiting_room\", \"message_text\": true, \"task\": $TASK_ID}" \
          localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/'

Open two browsers or two private tabs, log in with two different tokens and wait for the concierge bot to move both
users to a new room. The echo bot will also join this room and replies to every chat message.