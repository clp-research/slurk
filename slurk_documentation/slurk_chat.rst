.. _slurk_chat:

##################
Chat Webpage
##################

.. _chat:
.. figure:: slurk_chat.png
   :align: center
   :scale: 80 %

   Slurk Chat Window

:numref:`chat` shows the chat page that is provided by the web client.

Under the heading, the user is told which room he/she is currently in. The page itself
is divided into two sections: scrollable chat area, and are for multimodal input (images, for example).
At the bottom of the page, a text can be entered and sent to the server by pressing the ENTER key.

All messages appear on the chat page. If a message is shown in italics, this message can be only
seen for oneself. However, upon reload all previous messages are shown in italics, indicating that
they belong to the history of the chat at this point.

The multimodal input is filled with commands, which bots [1]_ react to.
If a message starts with ``/``, the message is interpreted as a command, and bot
reacts accordingly to it (displays an image, for example). If the command was not found,
the client is notified about this.

Other properties include list of the users and latency time on the upper right corner of the chat.
One can display them or hide them as well as modify various parts of the chat webpage.

For more information about available commands please go to :ref:`slurk_commands`

---------------------------------------------------------------------------

.. [1] *Bots* are artificial agents, which are required to be active in the game in order to
        coordinate the game process. Various Slurk-based projects use different bots, but ConciergeBot,
        for example, is the universal one for all of them, since it pairs up two players and creates
        a separate game room for them.
