#!/usr/bin/env bash
set -eu

# Reads the admin token from a docker container
# Environment variables:
#   SLURK_DOCKER: Docker container name to use

docker logs $SLURK_DOCKER 2> /dev/null | sed -n '/admin token:/{n;p;}'
