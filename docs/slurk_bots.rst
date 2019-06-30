.. _slurk_bots:

=========================================
Writing your own bots
=========================================

Bots are little client programms, which can both communicate with human clients and the server. By sending commands and responding to socket events they can perform various actions, e.g. sending messages, changing images shown to human clients, connecting clients to task rooms and handling dialogue tasks. Defining an experimental or data collection setting typically includes writing one or multiple bots.

There are some sample bots provided as examples, two of which are dissected and explained below.

Dissecting the minimal bot
~~~~~~~~~~~~~~~~~~~~~~~~~~

The minimal bot is an example for a bot able to perform basic tasks, such as sending messages and images to clients joining the current room or changing the image shown in the image area. Furthermore, the minimal bot can display and change user permissions.

The bot file has to be called providing the server URL and port as well as a valid login token as arguments. The bot is then connects to the server using the `connectWithToken` command within the LoginNamespace.

.. code-block:: python

    with SocketIO(args.chat_host, args.chat_port) as socketIO:
        login_namespace = socketIO.define(LoginNamespace, '/login')

        login_namespace.emit('connectWithToken', {
                             'token': args.token, 'name': "minimal bot"})

If the connection was successfull, the bot connects to the ChatNamespace:

.. code-block:: python

    # verify login status
    def on_login_status(self, data):
        global chat_namespace
        if data["success"]:
            chat_namespace = socketIO.define(ChatNamespace, '/chat')
        else:
            print("Could not login to server:", data['message'])
            sys.exit(1)

The methods defined within the ChatNamespace class determine which actions the minimal bot is able to perform in task rooms. All bot actions are triggered by either events emmitted by the server or slash commands typed in using the chat interface. A new event handler has to be defined within the ChatNamespace class for every event or command the bot should react to. The syntax is the same for both cases:

.. code-block:: python

    def on_event(self,data):
        do_something(data)

On joining the room, all slash commands are registered using the `listen_to` command:

.. code-block:: python

    def on_joined_room(self, data):
        self.emit("command", {'room': data['room']['id'], 'data': [
                  'listen_to', 'new_image_private']})
        self.emit("command", {'room': data['room']['id'], 'data': [
                  'listen_to', 'new_image_public']})
        # ...

Subsequently, event handlers for server events and registered slash commands are added to the namespace class. For example, the minimal bot can change the image visible to all clients in the room using the registered slash command. The following method is called every time a client submits `/new_image_public` via the chat interface:

.. code-block:: python

    def on_new_image_public(self, data):
        print(data)
        self.emit('set_attribute', {
            'room': data['room']['id'],
            'id': "current-image",
            'attribute': "src",
            'value': "https://picsum.photos/400/200?" + str(randint(1, 200000000))
        })

        self.emit('log', {'message': "I have received a command, wohoo \\o/"})
    print(f"new public image requested: {data}")

The minimal bot first changes the `src` attribute of the image with the id `current-image` to a random image URL using the `set_attribute` command. Then it sends a message to the task log.

Apart from changing image attributes, the minimal bot is able to send messages and image visible in the chat area using the `text` and `image` commands (private messages and images, if the user id of the intended receiver is provided). It can modify which parts of the interface are shown to users using the `update_permissions` command, and request the current permission information from the server (`get_permissions`). Finally, it can clear the chat history using the `clear_chat` command.

Dissecting the multi bot
~~~~~~~~~~~~~~~~~~~~~~~~

The multi bot and the minimal bot share a large part of their features. The overall structure, including the procedure for connecting to the server, is the same for both bots.

The main difference between the minimal bot and the multi bot lies in the latter not being bound to a single room. Unlike the minimal bot, the multi bot is able to join new task rooms once they are created, potentially being simultaneously active in multiple rooms. If the event `new_task_room` is emmited by the server, the multi bot sends the command `join_task` with the corresponding room id. After joining the respective room, slash commands are registered in the same way as for the minimal bot.

.. code-block:: python

    def on_new_task_room(self, data):
        print("hello!!! I have been triggered!")
        if data['task']['name'] != 'meetup':
            return

        room = data['room']
        print("Joining room", room['name'])
        self.emit('join_task', {'room': room['id']})
        self.emit("command", {'room': room['id'], 'data': [
                  'listen_to', 'new_image_private']})
        self.emit("command", {'room': room['id'], 'data': [
                  'listen_to', 'new_image_public']})
        self.emit("command", {'room': room['id'], 'data': [
                  'listen_to', 'end_meetup']})

Just as the minimal bot, the multi bot is able to change the images shown in the image area. Apart from that, it stores the ids of clients joining any room the multi bot is in. If the slash command `/end_meetup` is submitted, every client in the current room is sent back to the waiting room:

.. code-block:: python

    def on_end_meetup(self, data):
        print(data)
        for user in users[data['room']['id']]:
            print(user, "leaving room", data['room']['name'])
            self.emit('leave_room', {'room': data['room']['id'], 'user': user})
            self.emit('join_room', {'room': 1, 'user': user})
        self.emit('leave_room', {'room': data['room']['id']})

Interacting with layouts
~~~~~~~~~~~~~~~~~~~~~~~~

Bots can modify layouts in two ways: Setting texts and altering attribute values.

For this, two functions are provided:

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
     'room': room_id,
     'id': "image",
     'attribute': "src",
     'value': url)
   })
