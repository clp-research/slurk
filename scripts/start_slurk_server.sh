#!/bin/bash

# (re)start the server named slurky

if [ "$(docker ps -qa -f name=slurky)" ]
then
    if [ "$(docker ps -qa -f status=running -f name=slurky)" ];
    then
        echo 'there is a running slurky'
        sudo docker kill slurky
    fi

    echo 'there is a slurky (running or stopped)'
    sudo docker rm slurky
fi

# start docker container for slurk server
export SLURK_SERVER_ID=$(docker run --name=slurky -p 80:5000 -e SECRET_KEY=your-key -d slurk/server)
