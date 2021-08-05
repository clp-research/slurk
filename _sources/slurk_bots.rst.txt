.. _slurk_bots:

=========================================
Writing your own bots
=========================================

Bots are little client programs, which can both communicate with human clients and the server. By sending commands and responding to socket events they can perform various actions, e.g. sending messages, changing images shown to human clients, connecting clients to task rooms and handling dialogue tasks. Defining an experimental or data collection setting typically includes writing one or multiple bots.

There are some sample bots provided as examples, one of which is explained below.
The complete code to all bots can be found on `GitHub <https://github.com/clp-research/slurk-bots>`_.

Dissecting the concierge bot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The concierge bot is an example for a bot able to group up users and move them into a newly created room.

The bot has to be started with a valid token, user id and optionally with a server URL and Port.
The URL defaults to ``http://localhost``.



.. code-block:: python

    # create bot instance
    concierge_bot = ConciergeBot(args.token, args.user, args.host, args.port)
    # connect to chat server
    concierge_bot.run()

If the connection was successful, the bot now listens to the events emitted by the server.
Listening on events is straightforward with adding new functions to the ``register_callbacks`` method.

The bot has to be notified when a user joins or leaves the room. For this purpose it can listen to the ``status`` event. More detailed information on existing events can be found in the next section.

.. code-block:: python

    class ConciergeBot:
        sio = socketio.Client(logger=True)
        tasks = dict()

        def __init__(self, token, user, host, port):
            """This bot lists users joining a designated
            waiting room and sends a group of users to a task room
            as soon as the minimal number of users needed for the
            task is reached.
            :param token: A uuid; a string following the same pattern
                as `0c45b30f-d049-43d1-b80d-e3c3a3ca22a0`
            :type token: str
            :param user: id of a `User` object that was created with
            the token.
            :type user: int
            :param host: Full URL including protocol and hostname.
            :type host: str
            :param port: Port used by the slurk chat server.
            :type port: int
            """
            self.token = token
            self.user = user
            self.uri = host
            if port is not None:
                self.uri += f":{port}"
            self.uri += "/slurk/api"

            LOG.info(f"Running concierge bot on {self.uri} with token {self.token}")
            # register all event handlers
            self.register_callbacks()

        def run(self):
            # establish a connection to the server
            # for authorization, the token has to be provided in the headers
            self.sio.connect(
                self.uri,
                headers={"Authorization": f"Bearer {self.token}", "user": self.user},
                namespaces="/",
            )
            # wait until the connection with the server ends
            self.sio.wait()

        def register_callbacks(self):
            @self.sio.event
            def status(data):
                # we differentiate between "join" and "leave" events
                if data["type"] == "join":
                    # get the user who has joined the room
                    user = data["user"]
                    # read the task associated with the user
                    task = self.get_user_task(user)
                    # join the task, if it exists
                    if task:
                        self.user_task_join(user, task, data["room"])
                elif data["type"] == "leave":
                    user = data["user"]
                    task = self.get_user_task(user)
                    if task:
                        # leave the task as the user is not present anymore
                        self.user_task_leave(user, task)

        def user_task_join(self, user, task, room):
            """A connected user and their task are registered."""
            task_id = task["id"]
            user_id = user["id"]
            user_name = user["name"]
            # create/update entry for this task with the connected user
            # store the room, where the user waits
            self.tasks.setdefault(task_id, {})[user_id] = room

            # if we reach the required user number for a task
            # move those users into a new task room
            if len(self.tasks[task_id]) == task["num_users"]:
                # create a new task room
                new_room = self.create_room(task["layout_id"])
                # let every user join the new room and leave the old one
                for user_id, old_room_id in list(self.tasks[task_id].items()):
                    etag = self.join_room(user_id, new_room["id"])
                    self.delete_room(user_id, old_room_id, etag)
                # clear the task entry as the users are now moved
                del self.tasks[task_id]
                # notify the server, that a room was created, so bots can join this room as well
                self.sio.emit("room_created", {"room": new_room["id"], "task": task_id})
            # if we do not have enough users for a task, send the new user a message
            else:
                self.sio.emit(
                    "text",
                    {
                        "message":
                            f"### Hello, {user_name}!\n\n"
                            "I am looking for a partner for you, it might take "
                            "some time, so be patient, please...",
                        "receiver_id": user_id,
                        "room": room,
                        "html": True
                    },
                    callback=self.message_callback
                )

In order to verify emits, a callback is provided to every call. Every callback is invoked with a success flag as the
first argument and an optional error message as a second argument, passed only if the success flag is ``False``:

.. code-block:: python

    @staticmethod
    def message_callback(success, error_msg=None):
        if not success:
            LOG.error(f"Could not send message: {error_msg}")
            exit(1)
        LOG.debug("Sent message successfully.")

In order to verify requests, one can read out their status code. For an overview of all status codes that a request could possibly return and their meaning view :ref:`slurk_api`

.. code-block:: python

    def get_user_task(self, user):
        """Retrieve task assigned to user."""
        # for authorization the token has to be provided in the headers
        task = requests.get(
            f'{self.uri}/users/{user["id"]}/task',
            headers={"Authorization": f"Bearer {self.token}"}
        )
        if not task.ok:
            LOG.error(f"Could not get task: {task.status_code}")
            task.raise_for_status()
        LOG.debug("Got user task successfully.")
        return task.json()
