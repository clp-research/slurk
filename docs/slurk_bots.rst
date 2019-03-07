.. _slurk_bots:

=========================================
Writing your own bots
=========================================

Bots are little client programms, which can both communicate with human clients and the server. By sending commands and responding to socket events they can perform various actions, e.g. sending messages, changing images shown to human clients, connecting clients to task rooms and handling dialogue tasks. Defining an experimental or data collection setting typically includes writing one or multiple bots.

There are some sample bots provided as examples, two of which are dissected and explained in detail below.

Dissecting the minimal bot
~~~~~~~~~~~~~~~~~~~~~~~~~

The minimal bot is an example for a bot able to perform basic tasks, such as sending messages and images if new clients are joining the current room or changing the image shown in the image area. Furthermore, the minimal bot can change and display user permissions.

The bot file has to be called providing the server URL and port as well as a valid login token.

After importing the necessary python modules, the ChatNamespace class is defined. The methods defined within this class determin which actions the minimal bot is able to perform in chat rooms.

Dissecting the multi bot
~~~~~~~~~~~~~~~~~~~~~~~

The multi bot and the minimal bot share a large part of their features. The main difference is that the multi bot is able to switch to other task rooms once they are created, therefore it is not bound to a single room as the minimal bot. If the event `new_task_room` is emmited by the server, the multi bot sends the command `join_task` with the corresponding room id.

Apart from that, the multi bot is able to change the images shown in the image area, storing the ids of clients joining any room the multi bot is in, and terminating the current meetup session for all clients.

Interacting with layouts
~~~~~~~~~~~~~~~~~~~~~~~

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
