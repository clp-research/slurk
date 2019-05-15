.. _slurk_api:

=================================================
REST API for slurk
=================================================

Slurk provides a REST API. As authorization the token has to be provided. Data has to be passed as JSON. The responds
will also return as JSON.


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

* ``PUT /api/v2/rooms/<string:name>``

  Updates the room by name:

  =========================  =================================================================================
  ``label``                  Label of the room
  ``layout``                 ID of the layout
  ``name``                   Unique name of the room
  ``read_only``              ``True`` if the room is read only
  ``show_latency``           ``True`` if the latency is shown in the room
  ``show_users``             ``True`` if the current users are shown in the room
  ``static``                 ``True`` if this room can be selected as login room
  =========================  =================================================================================

* ``DELETE /api/v2/rooms/<string:name>``

  Deletes the room by name if no associations to the room exist. Otherwise an error is returend.