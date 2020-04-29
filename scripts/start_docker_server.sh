#!/bin/bash

export SLURK_SERVER_ID=$(docker run --name=slurky -p 80:5000 -e SECRET_KEY=your-key -d slurk/server)
