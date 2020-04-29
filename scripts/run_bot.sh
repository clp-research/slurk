#!/bin/bash

# run a bot

# You may modify this call by providing additional environment variables:
#
# - ``CHAT_HOST``: The host address (must include the protocol like "https://")
# - ``CHAT_PORT``: The port of the host
#
# Note that you have to pass ``--net="host"`` to docker in order to
# make ``http://localhost`` working.


TOKEN=$1
BOT=$2

if [ "$#" -eq 2 ]
then
  docker run -e TOKEN=$TOKEN --net="host" $BOT
else
  echo "You need to specify the bot token and the bot path"
  echo "Ex: 'sh $0 \$BOT_TOKEN slurk/echo-bot'"
fi
