#!/bin/bash

# restart the server named slurky

# stop running containers
sudo docker kill slurky
sudo docker rm slurky

# start docker container for slurk server
export SLURK_SERVER_ID=$(docker run --name=slurky -p 80:5000 -e SECRET_KEY=your-key -d slurk/server)
sleep 1
