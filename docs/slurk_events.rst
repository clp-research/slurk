.. _slurk_events:

##################
Slurk Events
##################


In the course of time different events are created.
These do not always contain the same parameters.
Optional parameters must be checked beforehand.
These are specified in the description.

* `status <type>`
    * a status update has been made
    * `timestamp`: The actual server time
    * `<type>`: Type of update
        * `new_image`: Ein new picture was sent
            * `sid`: Sender of the image
        * `join`: A client has connected to the room
            * `sid`: Session ID of the new client
            * `name`: Name of the new client
        * `leave`: A client has left the room
            * `sid`: Session ID of the client
            * `name`: Name of the client
        * `undefined_command`: The command sent could not be interpreted
            * `command`: The transmitted command

* `message`
    * `timestamp`: The actual server time
    * `sid`: Session ID of the sender
    * `name`: Name of the sender
    * `msg`: the message sent
    * `privateMessage`: Specifies whether this message is private (bool)

* `new_image <url>`
    * A new picture has been sent
    * url`: URL of the new image

* `acquire_sid <sid>`
    *    `sid`: the session ID of the current client

* `my_pong`
    * This event can be used for latency calculation, for example

* `start_typing`
    * The specified client has started typing
    * `sid`: Session ID of the client
    * `name`: Name of the client
    * `room`: room of the client
* `stop_typing`
    * The specified client has stopped typing
    * `sid`: Session ID of the client
    * `name`: Name of the client
    * `room`: room of the client

* `active_users <dict>`
    * `dict`: a user dictionary `Session id => Client name`
