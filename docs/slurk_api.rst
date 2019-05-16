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

* ``GET /api/v2/rooms/<string:name>``

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

* ``POST /api/v2/rooms/``

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

* ``PUT /api/v2/rooms/<string:name>``

  Updates the room by name:

  =========================  =================================================================================
  ``label``                  Label of the room
  ``layout``                 ID of the layout
  ``read_only``              ``True`` if the room is read only
  ``show_latency``           ``True`` if the latency is shown in the room
  ``show_users``             ``True`` if the current users are shown in the room
  ``static``                 ``True`` if this room can be selected as login room
  =========================  =================================================================================

* ``DELETE /api/v2/rooms/<string:name>``

  Deletes the room by name if no associations to the room exist. Otherwise an error is returned.


Logging
-------


* ``GET /api/v2/rooms/<string:name>/logs``

  Returns the log of the room by name:

  =========================  =================================================================================
  ``id``                     ID of the log entry
  ``date_created``           The date when the log entry was created
  ``date_modified``          The date when the log entry was modified
  ``event``                  The event type of the log entry
  ``user``                   User who has created the log entry
  ``data``                   Arbitrary data which is stored alongside the entry
  =========================  =================================================================================

* ``GET /api/v2/users/<int:id>/logs``

  Returns a mapping for log entries for rooms of the specified user:

  =========================  =================================================================================
  ``id``                     ID of the log entry
  ``date_created``           The date when the log entry was created
  ``date_modified``          The date when the log entry was modified
  ``event``                  The event type of the log entry
  ``room``                   Associated room
  ``data``                   Arbitrary data which is stored alongside the entry
  =========================  =================================================================================

* ``POST /api/v2/users/<int:id>/logs``

  Creates a new log entry for the specified user

  =========================  =================================================================================
  ``event`` *                The event type of the log entry
  ``room``                   The room to associate with the event
  ``data``                   Arbitrary data which is stored alongside the entry
  =========================  =================================================================================