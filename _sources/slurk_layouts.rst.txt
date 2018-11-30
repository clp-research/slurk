.. _slurk_layouts:

=========================================
Layouts and Plugins
=========================================

In Slurk you have the possibility to integrate your own layouts.
With layouts it is possible to modify the right side and specify a stylesheet.

A layout is a JSON file with a top level dictionary with the following keys:

- ``"title"``: String displayed in the header. If no title is specified, "Slurk" is used.
- ``"subtitle"``: String displayed under the title.
- ``"html"``: Consists of a list of further dictionaries or strings.
    Each dictionary represents an HTML node.  Each key in this dictionary corresponds to the attribute in an HTML tag. There are also two predefined tags: ``"layout-type"`` and ``"layout-content"``. ``"layout-type"`` corresponds to the name of the node, ``"layout-content"`` corresponds to the content between the opening and closing tag. For example

    .. code-block:: json

      {
        "layout-type": "span",
        "layout-content": "text",
        "id": "box"
      }

    corresponds to the HTML of ``<span id="box">Text</span>``
- ``"css"``: A dictionary, which is similar to a typical css stylesheet. Example:
    .. code-block:: json

       {
         "#image-area": {
           "align-content": "left",
           "margin": "50px 20px 15px"
         }
       }
- ``"script"``: Provides the ability to inject a script plugin into the chat. It consists of another dictionary, which maps different triggers to scripts. Scripts can either lie in *app/static/plugins* or can be passed by link. Example:

    .. code-block:: json

      {
        "incoming-message": "display-message",
        "submit-message": "send-message",
        "print-history": "plain-history"
      }

These are the currently defined triggers:

- ``"incoming-message"``: Called, when a new message arrives. These are the passed parameters
    - ``data.user``: The user, who has send the message
    - ``data.timestamp``: The timestamp of the message
    - ``data.privateMessage``: A boolean value if this was a direct message or visible to the room
    - ``data.msg`` (Optional): The message string the sent message if any
    - ``data.image`` (Optional): The image url of the sent message if any (Either ``data.msg`` or ``data.image`` are available)
    - ``data.width`` (Optional): The width of the sent image (available if ``data.image`` is set)
    - ``data.height`` (Optional): The height of the sent image (available if ``data.image`` is set)
- ``"submit-message"``: Called, when the user hits RETURN on the typing area
    - ``text``: The text which was entered in the typing area
    - ``current_user``: The user, which just hit RETURN
    - ``current_timestamp``: The current timestamp
- ``"print-history"``: Triggered, when the server sends the history of the chat on joining a room
    - ``element.type``: Type of the event. Either ``"text"``, ``"command"`` or ``"status"``
    - ``element.user``: The user who send the event
    - ``element.timestamp``: The timestamp of the event
    - ``element.msg`` (``"text"``): The message of the text event
    - ``element.receiver_id`` (``"text"``, Optional): The receiver id, if it was a private message
    - ``element.command`` (``"command"``): The command which was executed
- ``"print-history"``: Triggered, when the server sends the history of the chat on joining a room
- ``"document-ready"``: Inserted into the JQuery ``$(document).ready`` function
- ``"plain"``: Inserted as plain script into the chat

Additional, some functions are guarantied to exist:

- ``display_message(sender, time, message, privateMessage)``
- ``display_image(sender, time, url, width, height, privateMessage)``
- ``display_info(time, message)``
- ``submit_text(text)``
- ``submit_image(url, width, height)``
- ``submit_command(parameter)``