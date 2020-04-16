.. _slurk_bots:

=========================================
Writing your own bots
=========================================

Bots are little client programs, which can both communicate with human clients and the server. By sending commands and responding to socket events they can perform various actions, e.g. sending messages, changing images shown to human clients, connecting clients to task rooms and handling dialogue tasks. Defining an experimental or data collection setting typically includes writing one or multiple bots.

There are some sample bots provided as examples, two of which are dissected and explained below.

Dissecting the concierge bot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The concierge bot is an example for a bot able to group up users and move them into a newly created room.

The bot has to be started with a valid token and optionally with a server URL and Port. ``args`` are parameters to the
bot itself and consists of a host, a port, and a token. For authorization the token has to be provided in the headers:

.. code-block:: python

    socketIO = SocketIO(args.chat_host, args.chat_port,
                        headers={'Authorization': args.token, 'Name': 'Concierge Bot'},
                        Namespace=ChatNamespace)

If the connection was successful, the bot connects to the ``ChatNamespace``. From now on it listens to the events
emitted by the server. Listening on events is straight forward with adding new methods to the ``ChatNamespace`` class.

The bot has to be notified when a user joins or leaves the room:

.. code-block:: python

    # Called on `status` events
    def on_status(self, status):
        # We are interested in "join" and "leave" events.
        if status['type'] == 'join':
            # Get the user, who has joined a room
            user = status['user']
            # Read the task associated with the user
            task = self.get_user_task(user)
            if task:
                # Join the task, if any
                self.user_task_join(user, task, status['room'])
        elif status['type'] == 'leave':
            user = status['user']
            task = self.get_user_task(user)
            if task:
                # Leave the task as the user is not present anymore.
                self.user_task_leave(user, task)


    @staticmethod
    def get_user_task(user):
        # REST call to the server.
        task = requests.get(f"{uri}/user/{user['id']}/task", headers={'Authorization': f"Token {token}"})
        if not task.ok:
            print("Could not get user task")
            sys.exit(2)
        # Return the task as dictionary
        return task.json()


    def user_task_join(self, user, task, room):
        task_id = task['id']
        user_id = user['id']
        user_name = user['name']

        # Check if the bot is already aware if this task. If not create it
        if task_id not in self.tasks:
            self.tasks[task_id] = {}
        # The tasks are determined by the `task_id` and the `user_id`. We store the room, where the user is present.
        self.tasks[task_id][user_id] = room

        # If we reach the required user for the task, move those users into a new task room.
        if len(self.tasks[task_id]) == task['num_users']:
            # First of all, create a new task room
            new_room = self.create_room(task['name'], task['layout'])
            # Notify the server, that the room was created, thus bots can join this room as well.
            # This is needed as separate step, as the socketio interface is not connected to the REST API.
            self.emit("room_created", {'room': new_room['name'], 'task': task_id}, self.room_created_feedback)

            for user, old_room in self.tasks[task_id].items():
                # Let every user join the new room and leave the old one.
                self.emit("join_room", {'user': user, 'room': new_room['name']}, self.join_room_feedback)
                self.emit("leave_room", {'user': user, 'room': old_room}, self.leave_room_feedback)
            # clear the task as the users are now moved. This shouldn't be necessary, but let's stay conservative.
            del self.tasks[task_id]
        else:
            # If we don't have enough users for a task, send the new user a message
            self.emit('text', {'msg': f'Hello, {user_name}! I am looking for a partner for you, it might take some '
                               'time, so be patient, please...',
                               'receiver_id': user_id,
                               'room': room}, message_response)

In order to verify emits, a callback is provided to every call. Every callback is invoked with a success flag as the
first argument and an error message as second argument, if the success flag is ``False``:

.. code-block:: python

    @staticmethod
    def join_room_feedback(success, error=None):
        if not success:
            print("Could not join room:", error)
            sys.exit(4)
        print("user joined room")
        sys.stdout.flush()

    @staticmethod
    def leave_room_feedback(success, error=None):
        if not success:
            print("Could not leave room:", error)
            sys.exit(5)
        print("user left room")
        sys.stdout.flush()

    @staticmethod
    def room_created_feedback(success, error=None):
        if not success:
            print("Could not create task room:", error)
            sys.exit(6)
        print("task room created")
        sys.stdout.flush()

Joining newly created task rooms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the concierge bot creates a new room, it will move the assigned user to this room. In order to join those task
rooms as bot, they may listen to the ``new_task_room`` event just like the echo bot:


.. code-block:: python

    def on_new_task_room(self, data):
        if data['task'] == TASK_ID:
            self.emit("join_room", {'user': self.id, 'room': data['room']})

At the point where a task room has been opened, it compares the task id of the task room with the specified id and joins
the room.

Interacting with layouts
~~~~~~~~~~~~~~~~~~~~~~~~

Bots can modify layouts in two ways: Setting texts and altering attribute values.

For this, four events are provided:

- ``set_attribute``: Sets a javascript attribute to a new value. Those are the fields, which may be passed:
    - ``attribute``: The attribute to be updated
    - ``value``: The value to be set for the given attribute
    - ``id`` (Optional): The id of the element, which is going to be updated
    - ``class`` (Optional): The class of the element, which is going to be updated
    - ``element`` (Optional): The element type, which is going to be updated. Either ``id``, ``class`` or ``element`` is required.
    - ``receiver_id`` (Optional): Sends the attribute to this receiver only
    - ``room`` (Optional): Sends the attribute to this room. Either ``receiver_id`` or ``room`` is required
    - ``sender_id`` (Optional): The sender of the message. Defaults to the current user

- ``set_text``: Sets a html text element  by id to a new value. Those are the fields, which may be passed:
    - ``id``: The id of the text element, which is going to be updated
    - ``text``: The text to be set
    - ``receiver_id`` (Optional): Sends the text to this receiver only
    - ``room`` (Optional): Sends the text to this room. Either ``receiver_id`` or ``room`` is required
    - ``sender_id`` (Optional): The sender of the message. Defaults to the current user

- ``add_class``: Adds the html class to an element by id. Those are the fields, which may be passed:
    - ``id``: The id of the element, which is going to be updated
    - ``text``: The class to be added
    - ``receiver_id`` (Optional): Adds the class for this receiver only
    - ``room`` (Optional): Adds the class for all receivers in this room. Either ``receiver_id`` or ``room`` is required
    - ``sender_id`` (Optional): The sender of the message. Defaults to the current user

- ``remove_class``: Removes the html class from an element by id. Those are the fields, which may be passed:
    - ``id``: The id of the element, which is going to be updated
    - ``text``: The class to be removed
    - ``receiver_id`` (Optional): Removes the class for this receiver only
    - ``room`` (Optional): Removes the class for all receivers in this room. Either ``receiver_id`` or ``room`` is required
    - ``sender_id`` (Optional): The sender of the message. Defaults to the current user

If you want to change an image for example, you may use something like this:

.. code-block:: python

   self.emit('set_attribute', {
     'room': room,
     'id': "image",
     'attribute': "src",
     'value': url)
   })


Messages
~~~~~~~~

Bots can listen to messages with ``on_text_message`` and ``on_image_message``:

.. code-block:: python

    def on_text_message(self, data):
        do_something(data)

``data`` in ``on_text_message`` has this structure:

- ``msg``: the text, which was sent
- ``user``: dictionary of ``id`` and ``name`` of the user, who submitted the command
- ``room``: the id of the room, where the command was entered, or ``None``
- ``private``: ``True`` if this is a private message like direct messages. ``False`` otherwise
- ``timestamp``

.. code-block:: python

    def on_image_message(self, data):
        do_something(data)

``data`` in ``on_image_message`` has this structure:

- ``url``: URL of the image to display
- ``user``: dictionary of ``id`` and ``name`` of the user, who submitted the command
- ``room``: the id of the room, where the command was entered, or ``None``
- ``width``: the recommended width of the image
- ``height``: the recommended height of the image
- ``private``: ``True`` if this is a private message like direct messages. ``False`` otherwise
- ``timestamp``

Commands
~~~~~~~~

Commands are very similar to text message, but requires a dedicated permission. Commands are sent to a room and a bot
can listen to a command with ``on_command``:

.. code-block:: python

    def on_command(self, data):
        do_something(data)

``data`` has this structure:

- ``command``: the sent command
- ``user``: dictionary of ``id`` and ``name`` of the user, who submitted the command
- ``room``: the id of the room, where the command was entered, or ``None``
- ``timestamp``
