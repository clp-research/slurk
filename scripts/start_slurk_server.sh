#!/bin/bash

# (re)start the server named slurky

if [ "$(docker ps -qa -f name=slurky)" ]
then
    if [ "$(docker ps -qa -f status=running -f name=slurky)" ];
    then
        sudo docker kill slurky
    fi

    sudo docker rm slurky
fi

# start docker container for slurk server
export SLURK_SERVER_ID=$(docker run --name=slurky -p 80:5000 -e SECRET_KEY=your-key -d slurk/server)
