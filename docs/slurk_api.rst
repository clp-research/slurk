.. _slurk_api:

=================================================
REST API for slurk
=================================================

Slurk provides a REST API. As authorization the token has to be provided. Data has to be passed as JSON. The responds
will also return as JSON. Example:

.. code-block:: bash


  curl -X POST
       -H "Authorization: 00000000-0000-0000-0000-000000000000"
       -H "Content-Type: application/json"
       -H "Accept: application/json"
       -d '{"name": "test_room2", "label": "Test Raum", "static": false}'
       localhost:5000/api/v2/rooms

Token
-----

* ``GET /api/v2/tokens``

  Returns a list of tokens:

  =========================  =================================================================================
  ``id``                     ID of the token
  ``permissions``            List of permissions for the token
  ``room``                   Room to land in with this token
  ``source``                 Optional source string
  ``task``                   Task assigned to this token
  ``user``                   User associated with this token
  ``uri``                    URI to query this token
  =========================  =================================================================================

* ``GET /api/v2/token/<string:id>``

  Returns the layout by id:

  =========================  =================================================================================
  ``id``                     ID of the token
  ``permissions``            List of permissions for the token
  ``room``                   Room to land in with this token
  ``source``                 Optional source string
  ``task``                   Task assigned to this token
  ``user``                   User associated with this token
  =========================  =================================================================================

* ``POST /api/v2/token``

  Generates a new token:

  =============================  ===========================================================================================================
  ``room`` *                     Room to land when using this token as login
  ``user_query``                 Can query other users
  ``user_log_event``             Can create custom log events
  ``user_room_join``             Can make users join a room
  ``user_room_leave``            Can make users leave a room
  ``message_text``               Can send text messages
  ``message_image``              Can send images
  ``message_command``            Can submit commands
  ``message_broadcast``          Can broadcast messages
  ``room_query``                 Can query arbitrary rooms
  ``room_log_query``             Can query logs for an arbitrary rooms. Without this permission only the current room can be queried
  ``room_create``                Can create a room
  ``room_update``                Can update a rooms properties
  ``room_delete``                Can delete a room if there are no backrefs to it (tokens, users etc.)
  ``layout_query``               Can query layouts of arbitrary rooms. The layout from the rooms the user is in can always be queried
  ``task_create``                Can generate tasks. Needed to open the task form
  ``task_query``                 Can query tasks
  ``token_generate``             Can generate tokens
  ``token_query``                Can query tokens. The token from the current user can always be queried
  ``token_invalidate``           Can invalidate tokens
  ``token_remove``               Can remove tokens
  =============================  ===========================================================================================================


* ``DELETE /api/v2/token/<string:id>``

  Invalidates the token

User
----

* ``GET /api/v2/users``

  Returns a list of users:

  =========================  =================================================================================
  ``id``                     ID of the user
  ``name``                   Name of the user
  ``rooms``                  List of rooms, where the user is present
  ``session_id``             Session ID used by SocketIO
  ``token``                  Token associated with the user
  ``uri``                    URI to query this user
  =========================  =================================================================================

* ``GET /api/v2/user/<int:id>``

  Returns the specified user:

  =========================  =================================================================================
  ``id``                     ID of the user
  ``name``                   Name of the user
  ``rooms``                  List of rooms, where the user is present
  ``session_id``             Session ID used by SocketIO
  ``token``                  Token associated with the user
  =========================  =================================================================================

* ``GET /api/v2/tasks``

  Returns a list of tasks:

  =========================  =================================================================================
  ``id``                     ID of the task
  ``name``                   Name of the task
  ``num_users``              Number of user needed for this task
  ``layout``                 Layout used for task rooms
  ``tokens``                 Tokens associated with this task
  ``uri``                    URI to query this task
  =========================  =================================================================================


Task
----

* ``GET /api/v2/user/<int:id>/task``

  Returns the task for the specified user if any:

  =========================  =================================================================================
  ``id``                     ID of the task
  ``name``                   Name of the task
  ``num_users``              Number of user needed for this task
  ``layout``                 Layout used for task rooms
  ``tokens``                 Tokens associated with this task
  ``uri``                    URI to query this task
  =========================  =================================================================================

* ``GET /api/v2/tasks``

  Returns a list of tasks:

  =========================  =================================================================================
  ``id``                     ID of the task
  ``name``                   Name of the task
  ``num_users``              Number of user needed for this task
  ``layout``                 Layout used for task rooms
  ``tokens``                 Tokens associated with this task
  ``uri``                    URI to query this task
  =========================  =================================================================================

* ``GET /api/v2/task/<int:id>``

  Returns the specified user:

  =========================  =================================================================================
  ``id``                     ID of the task
  ``name``                   Name of the task
  ``num_users``              Number of user needed for this task
  ``layout``                 Layout used for task rooms
  ``tokens``                 Tokens associated with this task
  =========================  =================================================================================

* ``POST /api/v2/task``

  Creates a new task:

  =========================  =================================================================================
  ``name`` *                 Name of the task
  ``num_users`` *            Number of user needed for this task
  ``layout``                 Layout used for task rooms
  =========================  =================================================================================

* ``PUT /api/v2/task/<int:id>``

  Updates the specified task:

  =========================  =================================================================================
  ``name``                   Name of the task
  ``num_users``              Number of user needed for this task
  ``layout``                 Layout used for task rooms
  =========================  =================================================================================


Room
----

* ``GET /api/v2/rooms``

  Returns a list of rooms:

  =========================  =================================================================================
  ``current_users``          List of users currently in the room
  ``label``                  Label of the room
  ``layout``                 ID of the layout
  ``name``                   Unique name of the room
  ``read_only``              ``True`` if the room is read only
  ``show_latency``           ``True`` if the latency is shown in the room
  ``show_users``             ``True`` if the current users are shown in the room
  ``static``                 ``True`` if this room can be selected as login room
  ``tokens``                 List of tokens which are associated with this room
  ``users``                  List of users who were associated with this room at least once
  ``uri``                    URI to query this room
  =========================  =================================================================================

* ``GET /api/v2/room/<string:name>``

  Returns the room by name:

  =========================  =================================================================================
  ``current_users``          List of users currently in the room
  ``label``                  Label of the room
  ``layout``                 ID of the layout
  ``name``                   Unique name of the room
  ``read_only``              ``True`` if the room is read only
  ``show_latency``           ``True`` if the latency is shown in the room
  ``show_users``             ``True`` if the current users are shown in the room
  ``static``                 ``True`` if this room can be selected as login room
  ``tokens``                 List of tokens which are associated with this room
  ``users``                  List of users who were associated with this room at least once
  =========================  =================================================================================

* ``POST /api/v2/room``

  Creates a new room:

  =========================  =================================================================================
  ``name`` *                 Unique name of the new room
  ``label`` *                Label of the room
  ``layout``                 ID of the layout
  ``read_only``              ``True`` if the room is read only
  ``show_latency``           ``True`` if the latency is shown in the room
  ``show_users``             ``True`` if the current users are shown in the room
  ``static``                 ``True`` if this room can be selected as login room
  =========================  =================================================================================

* ``PUT /api/v2/room/<string:name>``

  Updates the room by name:

  =========================  =================================================================================
  ``label``                  Label of the room
  ``layout``                 ID of the layout
  ``read_only``              ``True`` if the room is read only
  ``show_latency``           ``True`` if the latency is shown in the room
  ``show_users``             ``True`` if the current users are shown in the room
  ``static``                 ``True`` if this room can be selected as login room
  =========================  =================================================================================

* ``DELETE /api/v2/room/<string:name>``

  Deletes the room by name if no associations to the room exist. Otherwise an error is returned.

Layouts
-------

* ``GET /api/v2/layouts``

  Returns a list of layouts:

  =========================  =================================================================================
  ``name``                   Unique name for the layout
  ``id``                     ID of the layout
  ``title``                  Title of the layout
  ``subtitle``               Subtitle of the layout
  ``html``                   HTML present in the layout
  ``css``                    CSS present in the layout
  ``tokens``                 List of tokens which are associated with this room
  ``script``                 Javascript present in this layout
  ``uri``                    URI to query this layout
  =========================  =================================================================================

* ``GET /api/v2/layout/<int:id>``

  Returns the layout by id:

  =========================  =================================================================================
  ``name``                   Unique name for the layout
  ``id``                     ID of the layout
  ``title``                  Title of the layout
  ``subtitle``               Subtitle of the layout
  ``html``                   HTML present in the layout
  ``css``                    CSS present in the layout
  ``tokens``                 List of tokens which are associated with this room
  ``script``                 Javascript present in this layout
  =========================  =================================================================================

* ``POST /api/v2/layout``

  Creates a layout from the layout data. See :ref:`slurk_layouts` for more parameters

* ``PUT /api/v2/layout``

  Updates the layout from the layout data. See :ref:`slurk_layouts` for more parameters



Logging
-------


* ``GET /api/v2/room/<string:name>/logs``

  Returns the log of the room by name:

  =========================  =================================================================================
  ``id``                     ID of the log entry
  ``date_created``           The date when the log entry was created
  ``date_modified``          The date when the log entry was modified
  ``event``                  The event type of the log entry
  ``user``                   User who has created the log entry
  ``data``                   Arbitrary data which is stored alongside the entry
  =========================  =================================================================================

* ``GET /api/v2/user/<int:id>/logs``

  Returns a mapping for log entries for rooms of the specified user:

  =========================  =================================================================================
  ``id``                     ID of the log entry
  ``date_created``           The date when the log entry was created
  ``date_modified``          The date when the log entry was modified
  ``event``                  The event type of the log entry
  ``room``                   Associated room
  ``data``                   Arbitrary data which is stored alongside the entry
  =========================  =================================================================================

* ``POST /api/v2/user/<int:id>/logs``

  Creates a new log entry for the specified user

  =========================  =================================================================================
  ``event`` *                The event type of the log entry
  ``room``                   The room to associate with the event
  ``data``                   Arbitrary data which is stored alongside the entry
  =========================  =================================================================================