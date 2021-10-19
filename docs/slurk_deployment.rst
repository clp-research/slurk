.. _slurk_deployment:

=========================================
Deployment of the system
=========================================

Environment variables
~~~~~~~~~~~~~~~~~~~~~

slurk reads a few environment variables for configuration. Because slurk is a flask application,
it reads ``FLASK_ENV`` and defaults to a more verbose logging, when ``FLASK_ENV=development``.
Also, the admin token is fixed to ``00000000-0000-0000-0000-000000000000`` and for RapiDoc,
the token is provided. To provide cookies, a secret key is required, which can be set with
``SLURK_SECRET_KEY``, which defaults to a random value. This implies that every time the
server is restarted, the cookies will be invalidated.

slurk is backed by a database. When no database is provided, an in-memory database is used.
This can be changed by setting ``SLURK_DATABASE_URI``. For a list of possible engines, see
`the SQLAlchemy documentation <https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls>`_,
however only SQLite and Postgres are tested. If you notice errors with other providers, please
`file an issue <https://github.com/clp-research/slurk/issues/new>`_. Also note, that
SQLite behaves weirdly when using auto-increment keys, so deletion of entries may cause the
same id to be used again. Later, we will see how slurk can be set up with a Postgres-database and
docker-compose.

The API of slurk uses ETags for patching, putting, and deleting entries. Those can be disabled
when setting ``SLURK_DISABLE_ETAG``.

OpenVidu support
----------------

When slurk should connect to an OpenVidu server, those additional variables may be set:

- ``SLURK_OPENVIDU_URL``: for example ``"https://openvidu.example.com"``
- ``SLURK_OPENVIDU_SECRET``: Secret used for the openvidu server
- ``SLURK_OPENVIDU_PORT``, defaults to ``443``
- ``SLURK_OPENVIDU_VERIFY``, Enable SSL validation, defaults to ``True``

For spinning up an OpenVidu server, please consult the `corresponding documentation <https://docs.openvidu.io/en/2.18.0/deployment/>`_.

Hosting slurk
~~~~~~~~~~~~~

There is a script in the slurk-repository called ``scripts/start_server.sh``. Depending
on the environment variables set, the script starts a GUnicorn server locally or in a
docker container. Please see the header of the script for the usage.

Docker
------

As described in :ref:`slurk_gettingstarted`, the easiest way is to use ``docker``.

.. code-block:: bash

  $ docker run -p 5000:80 slurk/server

Please note that passing an SQLite database also requires a volume to be bound when
the database should be persistent. For Postgres, make sure that the docker container
can access the same domain as the database.

Flask
-----

Flask provides several ways for hosting an application, for example

.. code-block:: bash

  $ export FLASK_APP=slurk
  $ flask run

See the `Deployment Options <https://flask.palletsprojects.com/en/2.0.x/deploying/>`_ of
Flask for a comprehensive list of different options.


Example using docker-compose and Postgres
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before spinning up slurk, we need a proper database. For our case, we chose postgres.
When using the postgres docker container and the slurk docker container, the two
containers probably can't see each other, so we use `docker-compose <https://docs.docker.com/compose/>`_ here.
We want to host slurk on port 5000 and connect it to the postgres database. The database
should be persistent, so a volume for the data has to be mounted. This is the
``docker-compose.yml`` file we end up with:

.. code-block:: yaml

  version: "3.9"

  services:
    db:
      image: postgres
      restart: always
      environment:
        - POSTGRES_PASSWORD=SUPER_SECRET_PSQL_PASSWORD
      volumes:
        - ./postgres-data:/path/to/postgres/data

    slurk:
      image: slurk/server
      restart: on-failure
      ports:
        - 5000:80
      environment:
        - SLURK_DATABASE_URI=postgresql://postgres:SUPER_SECRET_PSQL_PASSWORD@db:5432/postgres
        - SLURK_SECRET_KEY=MY_SLURK_SECRET_KEY
        - SLURK_OPENVIDU_URL=https://openvidu.example.com
        - SLURK_OPENVIDU_SECRET=MY_SUPER_SECRET_OV_SECRET

First, we start the postgres-container, named ``db``. We define the password to login
to the database and mount the database content to ``/path/to/postgres/data``.
When postgres has started, we pass the postgres URI to slurk, alongside a secret key.
As we also want OpenVidu support, the two required OpenVidu-variables are also passed.

Now follow these steps if you want to (re-)start slurk.

1. Navigate into the directory of your ``docker-compose.yml`` file.

2. Stop old containers and remove containers, networks, volumes and images created by ``up``.

.. code-block:: bash

  $ docker-compose down

3. Pull all associated docker images.

.. code-block:: bash

  $ docker-compose pull
   

4. (Optional) If you do not wish to use the default slurk from GitHub, you should manually build a slurk image of your preferred version afterwards. Start by navigating into your slurk project folder.

.. code-block:: bash

  $ docker build --tag "slurk/server" -f Dockerfile .

Navigate back to the directory of your ``docker-compose.yml`` file afterwards.

5. Start all specified containers in the background and leave them running.

.. code-block:: bash

  $ docker-compose up -d

6. (Optional) Verify that all containers have been successfully started.

.. code-block:: bash

  $ docker container ls -a

