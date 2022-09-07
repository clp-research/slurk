# Slurk & Webgazer

With this version of slurk you can run [Webgazer](https://webgazer.cs.brown.edu/), an application to track the user's eye movements.

## Quick Start
In order to start a demo you have to create a room with a task and add the ```gazer``` plugin to your task room (add it to the ```plain``` entry).
Right now this is nothing more than a demo, so you will see a red dot in the area of the screen where the Webgazer plugin thinks you are looking at.

## Observations
The Webgazer plugin seems to work for more general areas of the screen. It was tested with the click-bot to see whether it is possible to replace the click of a mouse by eye movement (eg. stare at the object for more than 3 seconds).
Unfortunately the prediction from the model does not seems to be precise enough to replace a mouse click.
The predicted coordinates show quite heavy "jumps" around the point where the user is actually looking at.

The Webgazer plugin seems to work however for less fine grained tasks (eg. is the user looking at the chat or the task part of the webpage? Given that the screen is divided in 4 sectors, which one is the user looking at?).

Finally it must be noted that the model can be fine-tuned during the task by simply looking at some point on the screen and clicking it with the mouse. This could be integrated as a preparation step for the task in order to improve the output of the model.