#!/usr/bin/env bash
set -eu

# Reads the admin token from a docker container
# Environment variables:
#   SLURK_DOCKER: Docker container name to use

for i in {1..10}; do
    logs=$(docker logs $SLURK_DOCKER 2>&1)
    if echo $logs | grep -q 'admin token'; then
        ADMIN_TOKEN=$(echo "$logs" | sed -n '/admin token/{n;p;}')
        break
    fi
    if echo $logs | grep -q ERROR; then
        exit 1
    fi
    sleep 1
done

if [ -z ${ADMIN_TOKEN+x} ]; then
    exit 2
fi

echo "$ADMIN_TOKEN"
