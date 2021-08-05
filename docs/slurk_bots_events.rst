.. _slurk_bots_events:

=========================================
Bot related Events
=========================================

Rooms
~~~~~
There are two types of events indicating that a new room was created. The first of the two ``new_room`` is the more general one. It can be triggered for every created room independently of its purpose and layout. Both events are received by all connected users.

.. code-block:: python

    @self.sio.event
    def new_room(data):
        do_something(data)

``data`` in ``new_room`` has this structure:

- ``room(int)``: the ``id`` of the room that was created

The second event can be triggered only if a task room was created. A task room is a room that has a ``task_id`` assigned. 

.. code-block:: python

    @self.sio.event
    def new_task_room(data):
        do_something(data)

``data`` in ``new_task_room`` has this structure:

- ``room(int)``: the ``id`` of the room that was created
- ``task(int)``: the ``id`` of the task that was assigned to the room
- ``users(list)``: a list of users that are linked to this task room. Each ``user(dict)`` is represented by an ``id(int)`` and a ``name(str)``

It is important to remember that those events are not sent automatically on room creation but have to be triggered by a bot after it has created a room:

.. code-block:: python

    self.sio.emit("room_created", data)

``data`` is a dictionary with the following keys:

- ``room(int)``: the ``id`` of the room that was created
- ``task(int, optional)``: the ``id`` of the task that will be performed in this room


Example: Echo Bot
-----------------
When the concierge bot creates a new room, it will move the assigned users to this room and send a ``room_created`` event to the server. In order to join those task rooms as a bot, they may listen to the ``new_task_room`` event just like the echo bot:

.. code-block:: python

        @self.sio.event
        def new_task_room(data):
            room_id = data["room"]
            task_id = data["task"]
            if self.task_id is None or task_id == self.task_id:
                response = requests.post(
                    f"{self.uri}/users/{self.user}/rooms/{room_id}",
                    headers={"Authorization": f"Bearer {self.token}"}
                )

If a task room has been opened, it compares the task id of the task room with its own task id. It joins the room only if the two task ids match or it is not assigned any task id. We interpret the latter as the echo bot being relevant to all tasks.

Movement
~~~~~~~~
Monitoring own movement
-----------------------

Bots can monitor their own movement between rooms. This includes them joining or leaving a room. For this purpose, they have to listen to the ``joined_room`` and ``left_room`` events, respectively. Both events are only sent to the user (e.g. bot) that caused them.

.. code-block:: python

    @self.sio.event
    def joined_room(data):
        do_something(data)

``data`` in ``joined_room`` has this structure:

- ``user(int)``: the ``id`` of the user who caused this event
- ``room(int)``: the ``id`` of the room that was entered by this user

Task bots are generally sent to rooms to instruct users and provide resources necessary to the task fulfillment. The ``joined_room`` event handler could be used to introduce the bot to the users and set an initial task description.

.. code-block:: python

    @self.sio.event
    def left_room(data):
        do_something(data)

``data`` in ``left_room`` has this structure:

- ``user(int)``: the ``id`` of the user who caused this event
- ``room(int)``: the ``id`` of the room that was left by this user

Monitoring overall movement
---------------------------
Bots are also notified once a user joins or leaves one of the rooms the bot is placed in. The term `user` here includes the bot itself, as well as other bots and human users.


.. code-block:: python

    @self.sio.event
    def status(data):
        do_something(data)

``data`` in ``status`` has this structure:

- ``type(str)``: the status type, either `join` or `leave`
- ``user(dict)``: dictionary of ``id(int)`` and ``name(str)`` of the user who caused this event
- ``room(int)``: the ``id`` of the room that was entered or left, respectively
- ``timestamp(str)``: as ISO 8601: ``YYYY-MM-DD hh:mm:ss.ssssss`` in UTC Time

Chat
~~~~
All of the events mentioned below can be either ``private`` or not. If an event is ``private`` it is only sent to a designated receiver. If this receiver is the bot, it receives the event. Otherwise it does not receive it. If an event is not ``private`` it can be seen by all users in the specified room.
Only bots should send private content, but for debugging purposes, you can use the chat interface and the following syntax to send private messages ``@<user_id> <text>`` or private images ``@<user_id> image: <url>``. Make sure that whoever is supposed to send private content is assigned the ``send_privately`` permission.

Messages
--------
Every data collection experiment evolves around users exchanging messages. Those can be sent by any user that is assigned the ``send_message`` or ``send_html_message`` permission. A bot may wish to verify message content, count messages until a certain milestone is reached or otherwise process user messages.
Messages can also be sent by bots:

.. code-block:: python

    self.sio.emit(
        "text",
        data
    )

``data`` is a dictionary with the following keys:

- ``message(str)``: the content of the text message
- ``room(int)``: the ``id`` of the room where the text message will be sent to
- ``receiver_id(int, optional)``: the ``id`` of the user that this message is directed at
- ``broadcast(bool, optional)``: ``True`` if the message should be transmitted to all connected users. ``False`` otherwise
- ``html(bool, optional)``: ``True`` if special html formatting should be applied to a message. This requires ``send_html_message`` permissions. ``False`` otherwise.

Messages cause an event on the server side that can be handled by bots:

.. code-block:: python

    @self.sio.event
    def text_message(data):
        do_something(data)

- ``message(str)``: the content of the text message
- ``user(dict)``: dictionary of ``id(int)`` and ``name(str)`` of the user who sent the message
- ``room(int)``: the ``id`` of the room where the message was sent
- ``private(bool)``: ``True`` if this was a private message meant for a single user. ``False`` otherwise
- ``broadcast(bool)``: ``True`` if the message should be transmitted to all connected users. ``False`` otherwise
- ``timestamp(str)``: as ISO 8601: ``YYYY-MM-DD hh:mm:ss.ssssss`` in UTC Time

Images
------
If given the appropriate rights ``send_image``, a user may send image data. Normally, only bots are supposed to do so. But for debugging purposes, it is possible to send images via the chat interface using the syntax ``image: <url>``.
Bots can send images like this:

.. code-block:: python

    self.sio.emit(
        "image",
        data
    )

``data`` is a dictionary with the following keys:

- ``url(str)``: URL of the image to display
- ``width(int, optional)``: the recommended width of the image. Defaults to 200
- ``height(int, optional)``: the recommended height of the image. Defaults to 200
- ``room(int)``: the ``id`` of the room where the image is sent
- ``receiver_id(int, optional)``: the ``id`` of the user that this image is directed at
- ``broadcast(bool, optional)``: ``True`` if the image should be transmitted to all connected users. ``False`` otherwise

Images cause an event on the server side that can be handled by bots:

.. code-block:: python

    @self.sio.event
    def image_message(data):
        do_something(data)

``data`` in ``image_message`` has this structure:

- ``url(str)``: URL of the displayed image
- ``width(int)``: the recommended width of the image or ``None`` 
- ``height(int)``: the recommended height of the image or ``None``
- ``user(dict)``: dictionary of ``id(int)`` and ``name(str)`` of the user who submitted the image
- ``room(int)``: the ``id`` of the room where the image was sent
- ``private(bool)``: ``True`` if this was a private image meant for a single user. ``False`` otherwise
- ``broadcast(bool)``: ``True`` if the image was transmitted to all connected users. ``False`` otherwise
- ``timestamp(str)``: as ISO 8601: ``YYYY-MM-DD hh:mm:ss.ssssss`` in UTC Time

Commands
--------
Commands are very similar to text messages, but they are only visible to bots. In order for a user to be able to send commands, they need the permission ``send_command``. Commands are normally sent by human users. For a chat message to be understood as a command, it needs to be prefixed by a slash ``/``.
It is, however, also possible for bots to send commands:

.. code-block:: python

    self.sio.emit(
        "message_command",
        data
    )

``data`` is a dictionary with the following keys:

- ``command(str)``: the command content
- ``room(int)``: the ``id`` of the room where the command is sent
- ``receiver_id(int, optional)``: the ``id`` of the user that this command is directed at
- ``broadcast(bool, optional)``: ``True`` if the message should be transmitted to all connected users. ``False`` otherwise

Commands cause an event on the server side that can be handled by bots:

.. code-block:: python

    @self.sio.event
    def command(data):
        do_something(data)

``data`` in ``command`` has this structure:

- ``command(str)``: the command content
- ``user(dict)``: dictionary of ``id(int)`` and ``name(str)`` of the user who sent the command
- ``room(int)``: the ``id`` of the room where the command was sent
- ``private(bool)``: ``True`` if this was a private command meant for a single user. ``False`` otherwise
- ``broadcast(bool)``: ``True`` if the command was transmitted to all connected users. ``False`` otherwise
- ``timestamp(str)``: as ISO 8601: ``YYYY-MM-DD hh:mm:ss.ssssss`` in UTC Time
