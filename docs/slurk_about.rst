.. _slurk_about:

=========================================
Slurk: What's this?
=========================================

Many fields of research have profited in the last years from the availability, through so-called "crowd working platforms", of a large pool of workers that can do small, web-based tasks. This has helped research in psychology as well as, dramatically so, research in artificial intelligence, where it made possible the collection of large amounts of labelled data from which models can be derived. While the common platforms offer templates for tasks such as image labelling or anwering questions, there a no such templates for dialogue tasks, where more than one participant is needed at the same time.

To facilitate web-based dialogue experiments, we built **slurk**. (Think: "slack for mechanical turk"...) Slurk is a chat server onto which human participants as well as "bots" can log on to interact. Conversations happen in *rooms*, which are closed off to each other: While the server can handle many separate conversations in parallel, a given user will only be in one room and hence in one conversation.

We were specifically interested in multimodal dialogues which involve more than just words. A paradigmatic example for such a type of dialogue would be a discussion about an image that is being shown to the users in a room. To enable such a setting, we distinguish in the interface presented to users between what we call the *display area*, where some media (e.g., an image) can be displayed, and the *chat* and *input* area, in which the chat history is shown and the user's utterance is being composed, respectively. This display area can be controlled by a bot, which might cause the display to change in response to what was said. Bots in slurk have far-reaching control over what human users in a room can type and over what they can see. This provides a way to specfiy and control a dialogue task programmatically.



.. _screenshot_image:
.. figure:: example_interaction.png
   :align: center
   :scale: 60 %

   An example with two human users, one bot, and an image being shown in the display area



Some basic concepts
~~~~~~~~~~~~~~~~~~~~

Room
  A collection of users (humans and bots) that can talk to each other. Human users are always in exactly one room.
Bots
  Bots are little client programms (written in python, and connecting to the slurk server via `socket.io`) that can enter rooms as well. Unlike human users, bots can be in several rooms, being responsible for handling certain dialogue *tasks*. Defining an experimental or data collection setting typically means writing a bot.
Slash-Commands
  Bots can register commands with the server, which the users can then use to control the bot. These commands are prefixed with a slash. E.g., `/new_image` could be such a command that user can use to effect something (here, it could trigger a change of what is shown in the display area).
Token
  To provide control over who is allowed to log into the chat (since we're not interested in running a public server here), access is regulated via tokens. Tokens need to be created in advance and link a user (who is logging in with the token) to a specific task / room type.
Waiting Room
  A special room, realised by the `pairup_bot`, where users wait until a pre-determined number of members is reached (lets say, 2), in which case all members are moved to a newly created task-specific room.
