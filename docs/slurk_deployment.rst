.. _slurk_deployment:

=========================================
Deploying the system
=========================================

Using docker
~~~~~~~~~~~~

The easiest way to deploy the system is using Docker. For this, ``docker`` is recommended: ::

  sudo apt-get install docker
  
In order to run the server on port 80, just run

  $ docker run -p 80:5000 -e SECRET_KEY=your-key -d slurk/server

These additional environment variables can be specified:

- ``DEBUG``: admin token is ``00000000-0000-0000-0000-000000000000``
- ``SQLALCHEMY_DATABASE_URI``: URI to the database, defaults to ``sqlite:///:memory:``
- ``SQLALCHEMY_TRACK_MODIFICATIONS``: Tracks modifications in the database
- ``SQLALCHEMY_ECHO``: Prints all executed commands to the database
- ``DROP_DATABASE_ON_STARTUP``: Database will be recreated on restart

If you don't want to run it detached, you may omit ``-d``.

Running the example bots
~~~~~~~~~~~~~~~~~~~~~~~~

There are Docker containers for all example bots. To run these bots using docker, type

  $ docker run -e TOKEN=your-token slurk/concierge-bot

- ``CHAT_HOST``: The host address (must include the protocol like "https://")
- ``CHAT_PORT``: The port of the host

Note, that you have to pass ``--net="host"`` to docker in order to make ``http://localhost`` working.


Manual setup
~~~~~~~~~~~~

If you don't want to use docker for whatever reason, you can also manually setup the server.

General description and requirements
------------------------------------

This section includes information on how to run Slurk on Nginx server (Ubuntu 18.04)
with SSL connection.

First, you have to be sure that Python3.6+ is installed on your machine. Please navigate to
``server`` and install required packages via executing::

  pip install -r requirements.txt

Also please make sure that your Ubuntu server is running on Nginx [1]_ and ``systemd`` package is installed.
Do not forget to check if UFW (Uncomplicated Firewall) is installed on your machine [2]_.

Serving Slurk with Gunicorn
---------------------------

You can serve our Flask application on a permanent basis.
Such setup will allow you to have faster connections which are automatic since you are not required to manually start
the process with Python, but Nginx will configure everything for you. Most of the instructions are taken or adopted from
`this tutorial <https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04>`_.

First, isolate your Flask application on your computer. For this you have to install *virtualenv* package.::

  sudo apt install python3-venv

Navigate to your project directory and create a new project environment there. Also activate the environment and
install required packages::

  cd ~/server
  python3.6 -m venv serverenv
  source serverenv/bin/activate
  pip install -r requirements.txt

Now, assuming that *gunicorn* and *flask* are already installed, we will create the WSGI entry point for our application.::

  nano ~/server/wsgi.py

The chat instance itself is created in ``~/server/app/__init__.py``, and that is why we will use this instance in our `wsgi.py` file.
Import this instance into the file, save and close it once you are finished::

  from app import create_app

  app = create_app(debug=True)

  if __name__ == "__main__":
      app.run()

Next step would be to configure Gunicorn, but first we should check if the application is served correctly [3]_::

  cd ~/server
  gunicorn --bind host:5000 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker wsgi:app

Visit you server's address with the port ``:5000`` and check if you see the login page.
If it functions properly, please press ``CTRL-C`` in your terminal window and deactivate your environment.

Now we have to create the systemd service unit file. It will allow Ubuntu to automatically start our application
once the machine boots.::

  sudo nano /etc/systemd/system/chat.service

Fill this service file with information about your application and adjust paths/variable names where required::

  [Unit]
  Description=Gunicorn instance to serve MeetUp
  After=network.target

  [Service]
  User=user
  Group=www-data
  WorkingDirectory=/home/user/server
  Environment="PATH=/home/user/server/serverenv/bin"
  ExecStart=/home/user/server/serverenv/bin/gunicorn --bind unix:myproject.sock -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -m 007 wsgi:app

  [Install]
  WantedBy=multi-user.target

Save and close this file. Now we will start the Gunicorn service and enable it so that it is active once our machine is booted::

  sudo systemctl start chat
  sudo systemctl enable chat

To be sure that it is active, check its status::

  sudo systemctl status chat

The output should be similar to the following::

  chat.service - Gunicorn instance to serve meetup
  Loaded: loaded (/etc/systemd/system/chat.service; enabled; vendor preset: enabled)
  Active: active (running) since Fri 2018-08-17 11:25:12 CEST; 4h 20min ago
  Main PID: 18101 (gunicorn)
  Tasks: 2 (limit: 4915)
  CGroup: /system.slice/chat.service
        ├─18101 /home/user/slurk/server/chatenv/bin/python3 /home/user/slurk/server/chatenv/bin/gunicorn --bind unix:chat.sock -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker
        └─18103 /home/user/slurk/server/chatenv/bin/python3 /home/user/slurk/server/chatenv/bin/gunicorn --bind unix:chat.sock -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker

Configuring Nginx
-----------------

At this point our Gunicorn application server must be actively running, and now we have to enable Nginx to accept requests for our application.
First, we will create a new server block configuration file in Nginx's `sites-available` directory::

  sudo nano /etc/nginx/sites-available/chat

We will have to specify location of our socket file, that serves the application
and include certificates which were created earlier [4]_::

  server {

      listen 5000 ssl default_server;
      listen [::]:5000 ssl default_server;

      server_name _;
      root /home/user/slurk/server/app;

      access_log /home/user/slurk/server/nginx_logs/nginx-access.log;
      error_log /home/user/slurk/server/nginx_logs/nginx-error.log;

      include snippets/certs.conf;
      include snippets/ssl-params.conf;

      location / {
          include proxy_params;
          proxy_pass http://unix:/home/user/slurk/server/chat.sock;

          }

      }

Do not forget to link this file to the ``sites-enabled`` directory::

  sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled

Test it for syntax errors and restart Nginx::

  sudo nginx -t
  sudo systemctl restart nginx

As the last step, adjust UFW setting once again, adding full access to the Nginx server::

  sudo ufw delete allow 5000
  sudo ufw allow 'Nginx Full'

When you navigate to your server's domain name, you should be able to see the login interface [5]_.

Congratulations! You have managed to fully deploy Slurk!

---------------------------------------------------------------------------

.. [1] There is a nice tutorial on `how to install Nginx on Ubuntu 18.04 <https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04>`_.

.. [2] A very detailed tutorial can be found here: `Initial Server Setup with Ubuntu 18.04 <https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04>`_.

.. [3] An important thing is that you specify type of the worker associated with the Gunicorn process. You should use websockets provided by `gevent` package:

      ``-k geventwebsocket.gunicorn.workers.GeventWebSocketWorker``

      More information can be found in `official Flask documentation <http://flask.pocoo.org/docs/1.0/deploying/wsgi-standalone/#gunicorn>`_.

.. [4] Different configurations require specification of static files' location,
       which include CSS files of your applications. In order to enable it, add additional
       location block where you specify location of the static files::

        location /static/ {
            alias /home/user/server/app/main/static/;
            }

.. [5] Regarding the port that you use: some ports are not accessible for the use (for example, ``7000`` is used for internal processes), so be careful when deciding which port to use.
       If you choose incorrect one, the application will not be accessible from outside of your network, even if you adjust firewall settings.
