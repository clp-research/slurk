.. _slurk_permissions:

=========================================
Security and Permissions
=========================================

Security and permissions are important aspects to consider when giving access to
bots and users. The permission should be set when creating tokens. For example, to
give the user access to write texts and commands in a room for a specific task, you can set ``send_message``
and ``send_command`` parameter during user token creation:

.. code-block:: bash

    $ curl -X POST \
       -H "Authorization: Token $ADMIN_TOKEN" \
       -H "Content-Type: application/json" \
       -H "Accept: application/json" \
       -d "{\"room\": \"waiting_room\", \"send_message\": true, \"send_command\": true, \"task\": $TASK_ID}" \
       localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/'

Here is a list of permissions that can be granted to a User (bot or human participant):

  =============================  ========================================================================
  ``send_message``               Can send text messages.
  ``send_html_message``          Can send html messages.
  ``send_command``               Can submit commands.
  ``send_image``                 Can send images.
  ``send_privately``             Can send private messages.
  ``receive_bounding_box``       Can receive bounding_box events
  ``broadcast``                  Can broadcast messages.
  ``openvidu_role``              OpenVidu role for the associated session ("SUBSCRIBER" or "PUBLISHER").
  =============================  ========================================================================

## Some notes:

- Commands can be used for text commands (e.g. "/done") or clickable buttons.
  In order to be able to issue them, a participant needs to have the
  ``send_message`` permission.
- The permissions ``send_html_message`` and ``receive_bounding_box`` are
  typically only given to bots.
- In order to receive bounding_box events, the bounding-boxes script needs to
  be enabled in the room layout.
