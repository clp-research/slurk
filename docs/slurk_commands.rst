.. _slurk_commands:


##################
Slurk Commands
##################

Slurk is based on `flask-SocketIO <https://flask-socketio.readthedocs.io/en/latest/>`_,
that is responsible for execution of clients' commands and their proper realisation.

If a message starts with a `/`, it is interpreted as a client command for communication
with the server. We will first analyse generally available client commands,
and then move on to the server commands, which are
needed for communication between bots and Slurk.

----------------
Client Commands
----------------

In addition to the commands registered by bots [1]_ , the following commands are also available for chatting:

* `/new_image <image-url> [room]`
    * A new image is sent to a room
    * `<image-url>` specifies the URL for the new image
    * The image is then displayed for the clients in the room on the righthand side

* `/listen_to <name>`
    * A command of listening to commands in the targeted room
    * If a client sends the command `name`, this client receives the command together with the entered parameters.

----------------
Server Commands
----------------

Bots communicate with the server using the server commands.
The commands are divided into two namespaces: `login` and `chat`.

The parameters are to be passed as a dictionary.

****************
Login Namespace
****************

* `connect_with_token <name> <room> [token]`
    * The client connects to a room
    * `name`: name of the client to be connected (e.g. "Bot-XY")
    * `room`: room to which the client should connect
    * `token`: authentication-token

****************
Chat Namespace
****************

* `my_ping`
    * A new event [2]_ (`my_pong`) is generated with the current bot
    * As an example, this command can be used to check latency level

* `disconnect`
    * Closes connection with the client

* `receive_sid`
    * The new event `acquire_sid` is created

* `log [params...]`
    * All parameters are written to the current log file

* `text <msg> [receiver]`
    * A text message is sent
    * `msg`: the message to be sent
    * `receiver`: message recipient. This can be a room or a session ID of the player.

* `command <name> [params...]`
    * The command is either executed or forwarded to the respective listeners.
    * `name`: name of the command
    * `params`: parameter to the command

* `clients`
    * The event `active_users` is created

---------------------------------------------------------------------------

.. [1] For information on bot-specific commands, please check REFERENCE

.. [2] `Events` are internal processes which are active within commands. For more please refer to REFERENCE
