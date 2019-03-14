.. _slurk_tools:

=========================================
Tools
=========================================

Currently there are two scripts in the `tools` directory: `start_server_and_bot.py` can be used to automatically start Slurk in combination with any number of bots provided as arguments. `start_clients.py` establishes client connections to the server using web browsers and client names specified in the config file.

The purpose of both scripts is to speed up the process of setting up new Slurk sessions, e.g. during the development of bots or plugins. In addition, they automatically handle basic configuration tasks for Slurk. This makes them a convenient starting point for new users.

The usage of both scripts is discribed below.

Start-up script for server and bots
~~~~~~~~~~~~~~~~~~~~~~~~~

Using the script `start_server_and_bot.py`, you can easily set up a new Slurk session on the localhost.
The script can be used by simply calling it with Python from the command line. If any virtual environment is needed to run Slurk, it has to be activated before executing the script.
You can provide any number of file paths to bot scripts as arguments in order to automatically connect the respective bots to the server.

By default, bots are connected to the Waiting Room. Using the flag `--testroom`, you can connect Bots to the Test Room instead. Without the `--testroom` argument, the PairupBot is connected by default. Adding `--nopairup` prevents the PairupBot from connecting.

Example: To start the server and connect both the PairupBot and the MultiBot (located in the `sample_bots` folder), you'd have to activate your virtual environment, navigate to the main directory of your Slurk installation, and call the startup script as follows:

.. code-block:: sh

    $ python tools/start_server_and_bot.py sample_bots/multi_bot.py


Start-up script for clients
~~~~~~~~~~~~~~~~~~~~~~~~~

`start_clients.py` can be used to automatically connect clients to a Slurk session. Before using the script, some information has to be provided to the `[tools]` within the config file. First, add the respective bash commands for the web browsers you want to use for connecting to the server (using the keys `browser1` and `browser2`). Then add names for the clients (using the key `client_names`). Multiple names can be provided, separated by commas. The number of names provided determines the number of clients to be connected to the server.

If you'd like to connect two clients to Slurk using Firefox and Chromium, the `[tools]` section of your config file might look like this:

.. code-block:: ini

    [tools]
    browser1 = firefox
    browser2 = chromium-browser
    client_names = John Zoidberg,Hubert Farnsworth

If everything is set up correctly, simply call `start_clients.py` with Python from the command line:

.. code-block:: sh

    $ python tools/start_clients.py

By default, clients are connected to the Waiting Room. Using the `--testroom` flag, you can connect clients to the Test Room instead.
