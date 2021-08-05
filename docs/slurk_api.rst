.. _slurk_api:



=================================================
REST API for slurk
=================================================

`View in RapiDoc <slurk_api_rapidoc.html>`_

slurk uses a RESTful API to modify the underlying database. In the link above, the full documentation
for each method is shown. When the slurk server is running, you can also visit ``/rapidoc``, ``/redoc``,
or ``/swagger-ui`` to see the API and try it out directly.

The API is more or less sorted in chronological order, as many tables require a previously returned
value.

Layouts, Rooms, and Tasks
-------------------------

A Layout defines how a room looks like. A room could either be a room, which is created by hand,
or it could be created from a task. For more information on layouts, have a look at :ref:`slurk_layouts`.

Users
-----

A user is a human user, mostly with very limited permissions, or a bot. Every user needs a
token to log in. While a token can register multiple users, it's not possible to assign more
than one token to a single user. Security and permissions are important aspects to consider when giving access to
bots and users. A token is associated with a permissions list and should only contain permissions,
which are really needed for the corresponding user (human or bot). Especially, the permissions to send
html messages have to be avoided when giving out to human users, as they allow users to inject arbitrary html objects into messages.

Also, the ``"api"``-permissions should not be given to arbitrary or unknown users, as with the api-token, everything
in the server can be accessed.

Logging
-------

Almost any action in slurk is logged to evaluate the experiment at a later point. The logging endpoint
can be used to filter for specific events or even add custom events.

Video and Audio
---------------

Besides sending images and text messages or change some attribute at the client, slurk can
connect to a `OpenVidu <https://docs.openvidu.io/en/2.19.0/>`_ server. To enable the
OpenVidu module, see :ref:`slurk_deployment`.
With OpenVidu enabled, the openvidu-endpoint is available. This implies that you never have to
talk to the OpenVidu-API directly, but can use slurk for this task. In order to let users communicate
with each other, the room has to be associated with an OpenVidu session. The session can be created
by the API. The returned id then has to be passed to the room, which is used for the call.
After connecting to the room, the server checks if a user may subscribe or publish to
the associated session. For this, they may have the ``"openvidu_role"`` ``"SUBSCRIBER"`` or ``"PUBLISHER"`` assigned
as permission.
