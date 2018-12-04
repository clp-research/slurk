.. _slurk_bots:

=========================================
Writing your own bots
=========================================

Disecting the minimal bot
~~~~~~~~~~~~~~~~~~~~~~~~~


Disecting the multi bot
~~~~~~~~~~~~~~~~~~~~~~~


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