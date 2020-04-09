.. _slurk_gettingstarted:

=========================================
Getting Started
=========================================

Building the documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to build the documentation yourself, you additionally need the packages *sphinx* and *sphinx_rtd_theme*. Then
you can create the documentation in the *docs* folder:

.. code-block:: sh

    pip install sphinx sphinx_rtd_theme
    cd docs
    make html

The generated documentation can then be found at *docs/_build/*

"Hello World": A basic test of the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to use system is using Docker. For this, ``docker`` is recommended:

.. code-block:: bash

  $ sudo apt-get install docker

In order to run the server on port 80 and store the container id, run

.. code-block:: bash

    $ SLURK_SERVER_ID=$(docker run -p 80:5000 -e SECRET_KEY=your-key -d slurk/server)

Read the admin token from the logs:

.. code-block:: bash

    $ ADMIN_TOKEN=$(docker logs $SLURK_SERVER_ID 2> /dev/null | sed -n '/admin token:/{n;p;}')

Verify you have a proper UUID token:

.. code-block:: bash

    $ echo $ADMIN_TOKEN
    b8b88080-b8d1-4eb2-af90-dccf7ece3d82

Create a room as landing page for our new token:

.. code-block:: bash

   $ curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d '{"name": "test_room", "label": "Test Room"}' \
          localhost/api/v2/room
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


Generate a new token for the clients (``sed`` removes quotation from JSON-string):

.. code-block:: bash

   $ curl -X POST \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          -d '{"room": "test_room", "message_text": true}' \
          localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/'
   9e6f53ae-2da7-4c53-92c7-ec43f8fa50cd

for a list of possible parameters see :ref:`slurk_api`

Visit http://localhost and enter whatever Name you like and this token, and click "enter chatroom".

This should transport you to the chat interface, where you then can happily type messages which no one will see (apart from you, that is).


.. _screenshot_void:
.. figure:: single_user.png
   :align: center
   :scale: 60 %

   A single user talking to no one in particular

This has confirmed that the server is working correctly, but so far this hasn't really been very exciting. So we move on.

.. _twobrowsers:

"Hello World" -- "Hello Other Browser": Testing with two browsers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the steps from the previous section (starting the server, creating a token and logging in), and then create an
addtional token and, **from a different web browser or in a private tab**, log in with that token. You should now see
both identities in the respective chat windows, and you should be able to talk with your two selves across these
browsers. Hurray!

(If your machine is set up in the right way [that is, the machine that is localhost is accessible from your network],
this might work across machines, and so you can have a chat with an actual different person.)

This has demonstrated the very basic capabilities -- providing a chat environment --, but so far there hasn't been any
use made of the display window. Let's change that by inviting a bot into our chat room.



Chatting with a bot
~~~~~~~~~~~~~~~~~~~

Without additional environment variables, the server uses an in-memory database and resets on every restart of the
server. Now let's restart the server to reset the database. Before we log onto the server in the way described above,
let us create a bot user and let it log on first. Create two tokens as described above, one for the user and one for
the bot.

There are Docker containers for all example bots. To run these bots using docker, type

.. code-block:: bash

   $ docker run -e TOKEN=$BOT_TOKEN --net="host" slurk/echo-bot

You may provide additional environment variables, too:
- ``CHAT_HOST``: The host address (must include the protocol like "https://")
- ``CHAT_PORT``: The port of the host

Note, that you have to pass ``--net="host"`` to docker in order to make ``http://localhost`` working.

Examining the log files
~~~~~~~~~~~~~~~~~~~~~~~

The point of all this, however, is not just to make interaction *possible*, it is to *record* these interactions to be
able to later study them or train models on them.

In order to read the logs, we use the API again:

.. code-block:: bash

   $ curl -X GET \
          -H "Authorization: Token $ADMIN_TOKEN" \
          -H "Content-Type: application/json" \
          -H "Accept: application/json" \
          localhost/api/v2/room/test_room/logs

The returned data contains, as a JSON list, most of the
events that the server handled, including all the messages that were sent. This should contain the information that you
need for your particular purposes.


This concludes the quick start. We now can be reasonably confident that the setup is working on your machine; and you
also got a first introduction to the basic concepts. But what we have seen so far would only allow us to run a single
room at a time. That may already be all you want if you conduct experiments locally with participants that you bring
into the lab. If you want to make use of crowdsourcing, though, you will want to be able to automatically pair up
participants and create task rooms for each pair. This will be explained in the next section.
