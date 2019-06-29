.. _slurk_api:

=================================================
REST API for slurk
=================================================

Slurk provides a REST API. As authorization the token has to be provided. Data has to be passed as JSON. The responds
will also return as JSON. Example::

  curl -X POST
       -H "Authorization: 00000000-0000-0000-0000-000000000000"
       -H "Content-Type: application/json"
       -H "Accept: application/json"
       -d '{"name": "test_room2", "label": "Test Raum", "static": false}'
       localhost:5000/api/v2/rooms

Token
-----

* ``POST /api/v2/token``

  Generates a new token:

  =============================  ===========================================================================================================
  ``room`` *                     Room to land when using this token as login
  ``user_query``                 Can query other users
  ``user_log_query``             Can query the logs for an arbitrary user, the logs the user is in can always be queried
  ``user_log_event``             Can create custom log events
  ``user_permissions_query``     Can query permissions of other user, the permissions for the current can always be queried
  ``user_permissions_update``    Can update permissions of a user
  ``user_room_query``            Can query the rooms for an arbitrary user, the rooms the user is in can always be queried
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
  ``room_close``                 Can close a room
  ``room_delete``                Can delete a room if there are no backrefs to it (tokens, users etc.)
  ``layout_query``               Can query layouts of arbitrary rooms. The layout from the rooms the user is in can always be queried
  ``task_create``                Can generate tasks. Needed to open the task form
  ``task_query``                 Can query tasks
  ``token_generate``             Can generate tokens
  ``token_query``                Can query tokens. The token from the current user can always be queried
  ``token_invalidate``           Can invalidate tokens
  ``token_remove``               Can remove tokens
  =============================  ===========================================================================================================


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

* ``POST /api/v2/room/``

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