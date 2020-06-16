.. _slurk_permission:

=========================================
Security and Permissions
=========================================

Security and permissions are important aspects to consider when giving access to 
bots and users. The permission should be set when creating tokens. For example, to 
give the user access to write texts and commands in a room for a specific task, you can set ``message_text`` 
and ``message_command`` parameter during user token creation:

.. code-block:: bash

    $ curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d "{\"room\": \"waiting_room\", \"message_text\": true, \"message_command\": true, \"task\": $TASK_ID}" \
       localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/'

Here is a list of permission that can be granted to bots/users:


  =============================  ===========================================================================================================
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


