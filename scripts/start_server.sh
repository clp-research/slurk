#!/usr/bin/env bash
set -eu

# Starts slurk on the local machine.
# Environment variables:
#   SLURK_SECRET_KEY: Secret key used for flask for cookies, defaults to `$RANDOM`
#   SLURK_DATABASE_URI: URI for the database, defaults to `sqlite:///slurk.db`
#   SLURK_PORT: Port to listen on, defaults to 5000
#   SLURK_DOCKER: Docker container name to be used. When not provided, docker is not used
#   SLURK_DOCKER_TAG: Docker tag to be used, defaults to `latest`
#   SLURK_ENV: Environment for flask, either `development` or `production`, defaults to `development`

export SLURK_SECRET_KEY=${SLURK_SECRET_KEY:-$RANDOM}
export SLURK_DATABASE_URI=${SLURK_DATABASE_URI:-sqlite:///slurk.db}
export FLASK_ENV=${SLURK_ENV:-development}
export FLASK_APP=slurk
PORT=${SLURK_PORT:-5000}

if [ -z ${SLURK_DOCKER+x} ]; then
    gunicorn -b :$PORT -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker 'slurk:create_app()'
else
    if ! command -v docker &> /dev/null; then
        echo '`docker` could not be found' 1>&2
        exit 2
    fi
    if ! command -v realpath &> /dev/null; then
        echo '`realpath` could not be found' 1>&2
        exit 2
    fi

    if [ "$(docker ps -qa -f name=$SLURK_DOCKER)" ]; then
        if [ "$(docker ps -qa -f status=running -f name=$SLURK_DOCKER)" ]; then
            docker kill $SLURK_DOCKER 2> /dev/null | true
        fi

        docker rm $SLURK_DOCKER 2> /dev/null | true
    fi

    if $(echo "$SLURK_DATABASE_URI" | grep -q '^sqlite:///'); then
        path=$(echo "$SLURK_DATABASE_URI" | sed 's#sqlite:///##')
        touch $path
        param="-e SLURK_DATABASE_URI=sqlite:///slurk.db -v $(realpath $path):/slurk.db"
    else
        param="-e SLURK_DATABASE_URI=$SLURK_DATABASE_URI"
    fi

    docker run -d \
        --name=$SLURK_DOCKER \
        -p $PORT:80 \
        -e SLURK_SECRET_KEY=$SLURK_SECRET_KEY \
        -e FLASK_ENV=$FLASK_ENV
        $param \
        slurk/server:${SLURK_DOCKER_TAG:-latest}
fi
