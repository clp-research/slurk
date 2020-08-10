.. _slurk_gettingstarted:

=========================================
Getting Started
=========================================

"Hello World": A basic test of the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to use system is using Docker (https://www.docker.com/products/docker-desktop). For this, ``docker`` is
recommended:

.. code-block:: bash

  $ sudo apt-get install docker

In order to run the server on port 80, store the container id, and
read the admin token, run:

.. code-block:: bash

    $ source scripts/start_slurk_server.sh
    $ source scripts/get_admin_token.sh

Verify you have a server id and proper UUID token (neither of these
should be empty):

.. code-block:: bash

    $ echo $SLURK_SERVER_ID
    $ echo $ADMIN_TOKEN

Create a room as landing page for our new token. In order to create a room,
specify the token, the room name (as identifier), and a label:

.. code-block:: bash

   $ sh scripts/create_room.sh $ADMIN_TOKEN test_room "Test Room"

This will return the room settings::

   {
     "current_users": {},
     "label": "Test Room",
     "layout": null,
     "name": "test_room",
     "read_only": false,
     "show_latency": true,
     "show_users": true,
     "static": false,
     "users": {}
   }

Generate a new token for the room you just created (the room
name). The clients need this token to log in:

.. code-block:: bash

   $ sh scripts/create_token.sh $ADMIN_TOKEN test_room

If you want to set other parameters see the :ref:`slurk_api` and
modify the script accordingly.

Visit http://localhost and enter whatever Name you like and the token
you generated, and click "enter chatroom".

This should transport you to the chat interface, where you then can
happily type messages which no one will see (apart from you, that is).


.. _screenshot_void:
.. figure:: single_user.png
   :align: center
   :scale: 60 %

   A single user talking to no one in particular

This has confirmed that the server is working correctly, but so far
this hasn't really been very exciting. So we move on.

.. _twobrowsers:

"Hello World" -- "Hello Other Browser": Testing with two browsers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the steps from the previous section (starting the server, creating
a token and logging in), and then create an additional token by
running the create_token script with the same parameters again. **From
a different web browser or in a private tab**, log in with that
token. You should now see both identities in the respective chat
windows, and you should be able to talk with your two selves across
these browsers. Hurray!

(If your machine is set up in the right way [that is, the machine that
is localhost is accessible from your network], this might work across
machines, and so you can have a chat with an actual different person.)

This has demonstrated the very basic capabilities – providing a chat
environment – but so far there hasn't been any use made of the display
window. Let's change that by inviting a bot into our chat room.


Chatting with a bot
~~~~~~~~~~~~~~~~~~~

Without additional environment variables, the server uses an in-memory
database and resets on every restart of the server. Now let's restart
the server to reset the database:

.. code-block:: bash

  $ source scripts/start_slurk_server.sh

You also need to reset the $ADMIN_TOKEN, and create the test room again:

.. code-block:: bash

  $ source scripts/get_admin_token.sh
  $ sh scripts/create_room.sh $ADMIN_TOKEN test_room "Test Room"

Before we log onto the server in the way described above, we need to
create a bot user and let it log on first. Create two tokens as
described above (if you used a different room name or label, make sure
to specify the correct ones). One of these tokens is for the user and one
is for the bot:

.. code-block:: bash

  $ sh scripts/create_token.sh $ADMIN_TOKEN test_room

There are Docker containers for all example bots. To run the echo-bot
using docker, you need to type the following, inserting your bot
token:

.. code-block:: bash

   $ sh scripts/run_echo_bot.sh TOKEN

After the bot has logged in, you can log yourself in as a user, using the
other generated token and seeing the bot perform.

Examining the log files
~~~~~~~~~~~~~~~~~~~~~~~

The point of all this, however, is not just to make interaction
*possible*, it is to *record* these interactions to be able to later
study them or train models on them.

In order to read the logs for our `test_room`, run:

.. code-block:: bash

   $ sh scripts/get_logs.sh $ADMIN_TOKEN test_room

The returned data contains, as a JSON list, most of the events that
the server handled, including all the messages that were sent. This
should contain the information that you need for your particular
purposes.

This concludes the quick start. We now can be reasonably confident
that the setup is working on your machine; and you also got a first
introduction to the basic concepts. But what we have seen so far would
only allow us to run a single room at a time. That may already be all
you want if you conduct experiments locally with participants that you
bring into the lab. If you want to make use of crowdsourcing though,
you will want to be able to automatically pair up participants and
create task rooms for each pair. This will be explained in the next
section.
