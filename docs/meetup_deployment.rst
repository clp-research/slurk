.. _meetup_depl:

MeetUp: how to deploy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The MeetUp task is dependent on displayed images, this is why the first step would be to
download the `ADE20k image dataset <http://groups.csail.mit.edu/vision/datasets/ADE20K/>`_. You will need training set in particular.
Navigate to your `/media` folder and arrange the image dataset there. This location will be used in Nginx server blocks.

If you want to use SSL connection, please make a new directory `certificates` in the project directory,
and populate it with your certificate and certificate key [1]_. Do not forget to restrict permissions to this directory
so that it can be only readable and accessible, but not writable.

Create a new file in your Nginx directory ``sudo nano /etc/nginx/snippets/certs.conf``
and set ``ssl_certificate`` and ``ssl_certificate_key`` directives there. Your ``certs.conf`` should look similar
to the next block:

.. code-block:: nginx

  ssl_certificate /home/user/project/certificates/cert.pem;
  ssl_certificate_key /home/user/project/certificates/key.pem;

You also need to configure strong encryption settings for SSL connection.
Please execute ``sudo nano /etc/nginx/snippets/ssl-params.conf`` and specify next parameters:

.. code-block:: nginx

  ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
  ssl_prefer_server_ciphers on;
  ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
  ssl_ecdh_curve secp384r1;
  ssl_session_cache shared:SSL:10m;
  ssl_session_tickets off;
  ssl_stapling on;
  ssl_stapling_verify on;

  resolver 8.8.8.8 8.8.4.4 valid=300s;
  resolver_timeout 5s;

  add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
  add_header X-Frame-Options DENY;
  add_header X-Content-Type-Options nosniff;

For more information, address `Nginx's HTTPS configuration <http://nginx.org/en/docs/http/configuring_https_servers.html>`_.

The next step would be to create a new server block where our Nginx will serve image directory.
Open a new server block in your default nginx configuration file, which can be found in ``/etc/nginx/sites-available``:

.. code-block:: nginx

  server {

      listen 8000 ssl http2 default_server;
      listen [::]:8000 ssl http2 default_server;

      include snippets/certs.conf;
      include snippets/ssl-params.conf;

      location / {
              root /media/ADE20K_2016_07_26/;
              autoindex on;
              try_files $uri $uri/ =404;
                 }

        }

This block takes SSL certificate and its key along with location of images, and serves it on the port 8000.

Do not forget to build symlinks between two directories: `sites-available` and `sites-enabled`, where the first one is used
to store your server configuration, while the latter enables your block. This can be done via the following command:

.. code-block:: bash

  sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled

Check if you UFW is active and allow incoming connections for the port that you use to serve images [2]_.

If everything has been set up properly, you will be able to access images by visiting ``host:8000``, depending on your host.
At the moment, all images are accessible `here <https://dsg.lili.uni-bielefeld.de:8000>`_.

---------------------------------------------------------------------------

.. [1] In some circumstances you might need to remove encryption from certificate private key. In this case, please use ``openssl`` to generate a new certificate key.

.. [2] A very detailed tutorial can be found here: `Initial Server Setup with Ubuntu 18.04 <https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04>`_.
