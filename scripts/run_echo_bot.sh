#!/bin/bash

# run the echo bot for the getting-started tutorial

TOKEN=$1

if [ "$#" -eq 1 ]
then
  docker run -e TOKEN=$TOKEN --net="host" slurk/echo-bot
else
  echo "You need to specify the bot token"
  echo "Ex: 'sh $0 \$BOT_TOKEN'"
fi
