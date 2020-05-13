.. _slurk_multibots:

Pairing up participants and running multiple rooms
==================================================

In the following steps you will learn how to let bots and human users enter the slurk waiting room where users will be
paired up and put into a new task-specific chatroom along with bots. We provided an example bot handling this mechanism:
The **concierge bot** moves human users and other bots from the waiting room to a taskroom.

Prerequisites
--------------

Install the ``jq`` command::

  $ sudo apt-get install jq

Start the server if it's not running already (it might ask for your computer's password):

.. code-block:: bash

  $ source scripts/start_slurk_server.sh
  $ source scripts/get_admin_token.sh

Check your admin token, you may need it later when running bots in different shells:

.. code-block:: bash

  $ echo $ADMIN_TOKEN

Create a waiting room and a task
----------------------------------

First of all, we need a waiting room and a task. For the waiting room, we submit the layout. Let's take the layout
provided in the slurk-bots repository:

.. code-block:: bash

   $ curl https://raw.githubusercontent.com/clp-research/slurk-bots/master/concierge/layout.json > waiting_room_layout.json

This layout now has to be pushed to the server:

.. code-block:: bash

  $ WAITING_ROOM_LAYOUT=$(sh scripts/push_room_layout.sh $ADMIN_TOKEN waiting_room_layout.json)

Ensure we have a valid id:

.. code-block:: bash

   $ echo $WAITING_ROOM_LAYOUT

We can now create the waiting room with the associated layout:

.. code-block:: bash

   $ sh scripts/create_room_with_layout.sh $ADMIN_TOKEN waiting_room "Waiting Room" $WAITING_ROOM_LAYOUT

The next step is to create a task. Each task contains information about the number of users required in order to start
the task:

.. code-block:: bash

   $ source scripts/create_task.sh $ADMIN_TOKEN "Echo Task" 2
   $ echo $TASK_ID


Assign bots to rooms
---------------------

Each bot needs a token in order to be run.
The token for the concierge bot is stored in ``CONCIERGE_BOT_TOKEN``:

.. code-block:: bash

  $ CONCIERGE_BOT_TOKEN=$(sh scripts/create_token.sh $ADMIN_TOKEN waiting_room --concierge)

The token for the echo bot is stored in ``ECHO_BOT_TOKEN``:

.. code-block:: bash

  $ ECHO_BOT_TOKEN=$(sh scripts/create_token.sh $ADMIN_TOKEN waiting_room --echo)
  $ echo $ECHO_BOT_TOKEN

Now start the concierge bot using the token you just created:

.. code-block:: bash

   $ docker run -e TOKEN=$CONCIERGE_BOT_TOKEN --net="host" slurk/concierge-bot

The concierge bot is joining the waiting room now. It waits for two users to join the waiting room, who both have the
specified task assigned. Once both have joined, the bot will create a new task room and move both users into that room.
We want the echo bot to join this task room as well. The concierge bot emits two events when creating a new task room:
``new_room`` and ``new_task_room``.

The echo bot is able to listen to those events. This bot has an optional ``ECHO_TASK_ID`` parameter, to listen to specific tasks to join. Let's start it:

.. code-block:: bash

   $ docker run -e TOKEN=$ECHO_BOT_TOKEN -e ECHO_TASK_ID=$TASK_ID --net="host" slurk/echo-bot

Create user tokens for the task
--------------------------------

Now let's create two user tokens (run the command twice) and specify the task:

.. code-block:: bash

   $ sh scripts/create_token_for_task.sh $ADMIN_TOKEN waiting_room $TASK_ID

Open two browsers or two private tabs, log in with two different tokens and wait for the concierge bot to move both
users to a new room. The echo bot will also join this room and reply to every chat message.
