.. _slurk_layouts:

=========================================
Layouts and Plugins
=========================================

In Slurk you have the possibility to integrate your own layouts.
With layouts it is possible to modify the display area on the right side and specify a stylesheet.

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
- ``"css"``: A dictionary which is similar to a typical css stylesheet. Example:
    .. code-block:: json

       {
         "#image-area": {
           "align-content": "left",
           "margin": "50px 20px 15px"
         }
       }
- ``"script"``: Provides the ability to inject a script plugin into the chat. It consists of another dictionary, which
  maps different triggers to scripts or a list of scripts. Scripts can either be a predefined one, or can be passed by
  link. Example:

    .. code-block:: json

      {
        "incoming-message": "display-message",
        "submit-message": "send-message",
        "print-history": "plain-history"
      }
- ``"external"``: A list of javascript links to load. Example:

    .. code-block:: json

      [
        "https://github.com/OpenVidu/openvidu/releases/download/v2.11.0/openvidu-browser-2.11.0.min.js"
      ]

Predefined scripts:
    - ``"display-text"``: Displays texts in the chat as they arrive
    - ``"display-image"``: Displays images in the chat as they arrive
    - ``"plain-history"``: Shows messages in the chat, which have arrived before login
    - ``"send-message"``: Sends text, images, and commands depending on the entered text
    - ``"typing-users"``: Displays the currently typing users in the ``#typing`` element
    - ``"ask-reload"``: A popup asks on page reload, if this is the desired action


These are the currently defined triggers:

- ``"incoming-text"``: Called when a new message arrives. These are the passed parameters
    - ``data.user``: The user who has sent the message
    - ``data.timestamp``: The timestamp of the message
    - ``data.private``: A boolean value if this was a direct message or visible to the room
    - ``data.message``: The message string of the sent message if any
- ``"incoming-image"``: Called when a new message arrives. These are the passed parameters
    - ``data.user``: The user who has sent the message
    - ``data.timestamp``: The timestamp of the message
    - ``data.private``: A boolean value if this was a direct message or visible to the room
    - ``data.image``: The image url of the sent message if any (Either ``data.message`` or ``data.image`` are available)
    - ``data.width``: The width of the sent image (available if ``data.image`` is set)
    - ``data.height``: The height of the sent image (available if ``data.image`` is set)
- ``"submit-message"``: Called when the user hits RETURN on the typing area
    - ``text``: The text which was entered in the typing area
    - ``current_user``: The user who just hit RETURN
    - ``current_timestamp``: The current timestamp
- ``"print-history"``: Triggered when the server sends the history of the chat on joining a room
    - ``element.event``: Type of the event. Either ``"text"``, ``"command"`` or ``"status"``
    - ``element.user``: The user who sent the event
    - ``element.timestamp``: The timestamp of the event
    - ``element.message`` (``"text"``): The message of the text event
    - ``element.receiver_id`` (``"text"``, Optional): The receiver id, if it was a private message
    - ``element.command`` (``"command"``): The command which was executed
- ``"document-ready"``: Inserted into the JQuery ``$(document).ready`` function
- ``"plain"``: Inserted as plain script into the chat
- ``"typing-users"``: Triggered when a user starts or stops typing
    - ``users``: A map of currently typing users, with its id as the key

Additionally, some functions are guaranteed to exist:

- ``display_message(sender, time, message, privateMessage)``
- ``display_image(sender, time, url, width, height, privateMessage)``
- ``display_info(time, message)``
- ``submit_text(text)``
- ``submit_image(url, width, height)``
- ``submit_command(parameter)``




******************************
Layout development in practice
******************************

Creating and adding your own layout to Slurk allows you to customize the design and functionality of the waiting and
chat room without changing the static HTML and CSS files. It is possible to define and format new tags or to work with
existing ones.

The following steps demonstrate how to build your own layout for an example waiting room used by the concierge bot.

The waiting room is supposed to have a custom title, an image on the right, and a blue theme:

    .. code-block:: json

        {
          "title": "Waiting Room",
          "subtitle": "waiting for other players...",
          "html": [
            {
              "layout-type": "div",
              "id": "image-area",
              "layout-content": [
                {
                  "layout-type": "image",
                  "id": "current-image",
                  "src": "https://media.giphy.com/media/tXL4FHPSnVJ0A/giphy.gif",
                  "width": 500,
                  "height": 400
                }
              ]
            }
          ],
          "css": {
            "header, footer": {
              "background": "#115E91"
            },
            "#image-area": {
              "align-content": "left",
              "margin": "50px 20px 15px"
            }
          },
          "scripts": {
            "incoming-text": "display-text",
            "incoming-image": "display-image",
            "submit-message": "send-message",
            "print-history": "plain-history"
          }
        }
