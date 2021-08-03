.. _slurk_multibots:

Pairing up participants and running multiple rooms
==================================================

In the following steps you will learn how to let bots and human users enter the slurk waiting room where users will be
paired up and put into a new task-specific chatroom along with bots. We provide an example bot handling this mechanism:
The **concierge bot** moves human users from the waiting room to a task room.

Create a waiting room and a task
----------------------------------

First of all, we need a waiting room and a task. For the waiting room, we submit the layout. Let's take the one
provided in the slurk-bots repository:

.. code-block:: bash

   $ curl https://raw.githubusercontent.com/clp-research/slurk-bots/master/concierge/waiting_room_layout.json > waiting_room_layout.json

This layout now has to be pushed to the server:

.. code-block:: bash

  $ WAITING_ROOM_LAYOUT_ID=$(scripts/create_layout.sh waiting_room_layout.json | jq .id)
  
Ensure we have a valid id (should return an integer):

.. code-block:: bash

   $ echo $WAITING_ROOM_LAYOUT_ID

We can now create the waiting room with the associated layout:

.. code-block:: bash

   $ WAITING_ROOM_ID=$(scripts/create_room.sh $WAITING_ROOM_LAYOUT_ID | jq .id)

The next step is to create a task. You may wish to use a special layout for the task room.
Each task contains information about the number of users required in order to start the task (here 2):

.. code-block:: bash

   $ TASK_LAYOUT_ID=$(scripts/create_layout.sh examples/simple_layout.json | jq .id)
   $ TASK_ID=$(scripts/create_task.sh  "Echo Task" 2 $TASK_LAYOUT_ID | jq .id)

Assign bots to rooms
---------------------

Each bot has special permissions that it requires. For our example bots those are provided as JSON files.

.. code-block:: bash

  $ curl https://raw.githubusercontent.com/clp-research/slurk-bots/master/concierge/concierge_bot_permissions.json > concierge_bot_permissions.json
  $ curl https://raw.githubusercontent.com/clp-research/slurk-bots/master/echo/echo_bot_permissions.json > echo_bot_permissions.json

The token for the concierge bot is stored in ``CONCIERGE_TOKEN``. The associated user is stored in ``CONCIERGE_USER``:

.. code-block:: bash

  $ CONCIERGE_TOKEN=$(scripts/create_room_token.sh $WAITING_ROOM_ID concierge_bot_permissions.json | jq -r .id)
  $ echo $CONCIERGE_TOKEN
  $ CONCIERGE_USER=$(scripts/create_user.sh "ConciergeBot" $CONCIERGE_TOKEN | jq .id)
  $ echo $CONCIERGE_USER

The token for the echo bot is stored in ``ECHO_TOKEN``. The associated user is stored in ``ECHO_USER``:

.. code-block:: bash

  $ ECHO_TOKEN=$(scripts/create_room_token.sh $WAITING_ROOM_ID echo_bot_permissions.json | jq -r .id)
  $ echo $ECHO_TOKEN
  $ ECHO_USER=$(scripts/create_user.sh "EchoBot" $ECHO_TOKEN | jq .id)
  $ echo $ECHO_USER

Open two new terminals and copy ``CONCIERGE_TOKEN`` & ``CONCIERGE_USER`` to one terminal and ``ECHO_TOKEN`` & ``ECHO_USER`` & ``TASK_ID`` to another terminal.
Now start the concierge bot using the token you just created from the new terminal:

.. code-block:: bash

   $ docker run -e SLURK_TOKEN=$CONCIERGE_TOKEN -e SLURK_USER=$CONCIERGE_USER -e SLURK_PORT=5000 --net="host" slurk/concierge-bot

The concierge bot is joining the waiting room now. It waits for two users to join the waiting room, who both have the
same task assigned. Once both have joined, the bot will create a new task room and move both users into that room.
We want the echo bot to join this task room as well.

This bot has an optional ``ECHO_TASK_ID`` parameter, to listen to specific tasks to join. Let's start it 
from the new terminal that contains the echo bot token:

.. code-block:: bash

   $ docker run -e SLURK_TOKEN=$ECHO_TOKEN -e SLURK_USER=$ECHO_USER -e SLURK_PORT=5000 -e ECHO_TASK_ID=$TASK_ID --net="host" slurk/echo-bot

Create user tokens for the task
--------------------------------

Now let's create two user tokens from the original terminal (run the command twice) and specify the task:

.. code-block:: bash

   $ scripts/create_room_token.sh $WAITING_ROOM_ID examples/message_permissions.json 1 $TASK_ID | jq .id | sed 's/^"\(.*\)"$/\1/'

The last part of the command beginning with sed strips quotation marks from the token.
Open two browsers or two private tabs, log in with two different tokens and wait for the concierge bot to move both
users to a new room. The echo bot will also join this room and reply to every chat message.
