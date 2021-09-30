.. _slurk_layouts:

=========================================
Layouts and Plugins
=========================================

In slurk you have the possibility to integrate your own layouts.
With layouts, it is possible to modify the display area on the right side and specify a stylesheet.

A layout is a JSON file with a top-level dictionary. Besides the fields listed in the :ref:`slurk_api`
there are three fields, which are worth pointing out:

- ``"html"``: Comprises a list of further dictionaries or strings.
    Each dictionary represents an HTML node.  Each key in this dictionary corresponds to the attribute in an HTML tag. There are also two predefined tags: ``"layout-type"`` and ``"layout-content"``. ``"layout-type"`` corresponds to the name of the node, ``"layout-content"`` corresponds to the content between the opening and closing tag. For example

    .. code-block:: json

      {
        "layout-type": "span",
        "layout-content": "Text",
        "id": "box"
      }

    corresponds to the HTML of ``<span id="box">Text</span>``.
    It's also possible to nest the content. The following object will cause
    ``<span id="outer"><span id="inner">Text</span></span>``:

    .. code-block:: json

      {
        "layout-type": "span",
        "layout-content": {
          "layout-type": "span",
          "layout-content": "Text",
          "id": "inner"
        },
        "id": "outer"
      }

- ``"css"``: A dictionary which is like a typical CSS stylesheet. Example:
    .. code-block:: json

       {
         "#image-area": {
           "align-content": "left",
           "margin": "50px 20px 15px"
         }
       }

  This is injected as the following stylesheet:

    .. code-block:: css

      #image-area {
        align-content: left
        margin: 50px 20px 15px
      }

- ``"script"``: Provides the ability to inject a script plugin into the chat. It comprises another dictionary, which
  maps different triggers to scripts or a list of scripts. Scripts can either be a pre-defined one or can be passed by
  link. Example:

    .. code-block:: json

      {
        "incoming-text": "display-text",
        "submit-message": "send-message",
        "print-history": "plain-history"
      }

Triggers
~~~~~~~~

A full list of keys is shown in the :ref:`slurk_api`. There are some pre-defined scripts
which can be used. Also, several variables may be defined in a trigger:

``"incoming-text"``
-------------------
Displays text messages as they arrive

Variables:
  - ``data.user``: The user who has sent the message
  - ``data.timestamp``: The timestamp of the message
  - ``data.private``: A boolean value showing whether this was a direct message or visible to the room
  - ``data.message``: The message string of the sent message if any
  - ``data.html``: Tag if the message is marked as HTML
Examples:
  - ``"display-text"``: Prints as plain text
  - ``"markdown"``: Prints as formatted markdown if tagged as html

``"incoming-image"``
--------------------
Displays images in the chat area as they arrive

Variables:
  - ``data.user``: The user who has sent the message
  - ``data.timestamp``: The timestamp of the message
  - ``data.private``: A boolean value showing whether this was a direct message or visible to the room
  - ``data.image``: The image URL
  - ``data.width``: The width of the sent image
  - ``data.height``: The height of the sent image
Examples:
  - ``"display-image"``: Displays a simple image

``"submit-message"``
--------------------
Called when the user hits RETURN on the typing area

Variables:
  - ``text``: The text which was entered in the typing area
  - ``current_user``: The user who just hit RETURN
  - ``current_timestamp``: The current timestamp
Examples:
  - ``"send-message"``: Sends plain text and commands depending on the entered text

``"print-history"``
-------------------
Shows previous messages in the chat area after joining a room

Variables:
  Not all variables in ``element.data`` may be defined

  - ``element.event``: Type of the event
  - ``element.user``: The user who sent the event
  - ``element.timestamp``: The timestamp of the event
  - ``element.data.message``: The message of the text event
  - ``element.data.url``: The URL of an image
  - ``element.data.width``: The width of an image
  - ``element.data.height``: The height of an image
  - ``element.receiver``: The receiver, if it was a private message
  - ``element.command``: The command which was executed
Examples:
  - ``"plain-history"``: As plain text and images
  - ``"markdown-history"``: Formatted as markdown if tagged as html
  - ``"attribute-history"``: Applies previous changes to the layout

``"typing-users"``
------------------
Called when the state of currently typing users is changed

Variables:
  - ``users``: A map of currently typing users, with their ids as keys
Examples:
  - ``"typing-users"``: Shows which users are currently typing

``"plain"``
-----------
Injected as a script file into the site

Examples:
  - ``"ask-reload"``: A pop-up asks on page reload if this is the desired action
  - ``"enforce-fullscreen"``: Page content is grayed out, until a button is clicked that sends user into fullscreen. See ``enforce-fullscreen_layout.json`` in ``examples`` for an example layout
  - ``"bounding-boxes"``: Makes it possible for users to draw rectangles inside a designated drawing area (html element with the id ``drawing-area``). Per default, drawn rectangles are not shared between users inside a room. If you wish for all users in a room to share a common canvas give all users inside the room the permission ``receive_bounding_box``
  - ``"mouse-tracking"``: Mouse movement and clicks inside the designated html element with the id ``tracking-area`` are registered. They can be handled by bots through the ``mouse`` event.

``"document-ready"``
--------------------
Called when the document is loaded

Variables:
  - Everything defined from ``"plain"``

Additionally, some functions are guaranteed to exist:

- ``display_message(sender, time, message, privateMessage)``
- ``display_image(sender, time, url, width, height, privateMessage)``
- ``display_info(time, message)``
- ``submit_text(text)``
- ``submit_image(url, width, height)``
- ``submit_command(parameter)``


Layout development in practice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
