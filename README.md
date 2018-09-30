Botsi
=====

Please find the German documentation below. 

This project provides the server and the web client for the Botsi project to the
Order.

Getting started
---------------

The following is a simple walk through for how start the server and have a simple chat interaction with a bot, locally on your machine.
As the intended purpose is to run this on AMT, the process is a bit convoluted and involves a number of steps that might not seem entirely intuitive :-).
Instructions for writing your own bots can be found in sample_bots/how_to_bots.md

* set up a virtual environment for this project and install the requirements:

> virtualenv -p python3.6 slurkenv
> source slurkenv/bin/activate
> pip install -r requirements.txt


* start the server

> python chat.py


* generate token for the bot 
    * open http://127.0.0.1:5000/token in web browser
    * copy the generated token to your clipboard


* start bot

> python sample_bots/parrot.py TOKEN
(replace TOKEN with the token generated in the previous step)


* generate token for the player
    * open http://127.0.0.1:5000/token in web browser
    * for players: Source - anything, Room - Test Room, Task - meetup, Reusable - No
    * copy the generated token to your clipboard


* connect as player
    * open http://127.0.0.1:5000 in web browser
    * type in any name and paste the token into the field below ('None' as placeholder)