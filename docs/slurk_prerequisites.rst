.. _slurk_prerequisites:

=========================================
Prerequisites
=========================================

Slurk was developed and tested on UNIX-systems only. We therefore recommend using it on such or using WSL for Windows.
The easiest way to use the system is using Docker. For this, ``docker`` is recommended.

- If you are operating on Ubuntu, then follow :ref:`label-install-ubuntu`
- If you are operating on Windows 10, then follow :ref:`label-install-wsl`

For other operating systems, please see the `official docker documentation <https://docs.docker.com/get-docker/>`_.

.. _label-install-wsl:

Prepare Windows 10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker cannot easily run on Windows by default. Thus we enable the Windows Subsystem for Linux.
Make sure that Windows 10 has the latest updates installed:

+ For x64 systems: Version 1903 or higher, with Build 18362 or higher.
+ For ARM64 systems: Version 2004 or higher, with Build 19041 or higher.

.. note::

    This guide follows the `official WSL2 documentation <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_, so have a look into these for more details.
    These instructions use experimental features for Docker on Windows and thus could be outdated at any time.
    Furthermore, this guide is a response to a `Problem with getting an admin token (Ubuntu on WSL) <https://github.com/clp-research/slurk/issues/99>`_.

Setting up WSL 2
------------------------------

1. Type "PowerShell" into the search field. Right-click on the Windows PowerShell and then select *run as administrator*.
2. Enable WSL with the following command:

.. code-block:: bash

    $ dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

3. Upgrade to WSL2 with the following command:

.. code-block:: bash

    $ dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

4. Restart the system

5. Download the `Linux Kernel update package <https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi>`_

6. Double-click the update package downloaded in the previous step. Follow the installation steps.

7. (Optional) If step 6 results in an error *update only applies to machines with the Windows subsystem for Linux*: Type into the search field "Turn Windows features on or off". Open the program. Deselect *Virtual Machine Platform* and *Windows Subsystem for Linux* and click OK. Restart your system. Open the program again and this time select *Virtual Machine Platform* and *Windows Subsystem for Linux* and click OK. Restart your system. Try running step 6 again.

8. Set WSL2 as the default for linux distributions:

.. code-block:: bash

    $ wsl --set-default-version 2

Install Ubuntu-20.04.1 using the App Store
------------------------------------------

1. After the installation is complete click *Launch*
2. Set a Unix username and password
3. Open a Powershell
4. Check the used WSL version for each distribution using PS:

.. code-block:: bash

    $ wsl --list --verbose
      NAME                   STATE           VERSION
      Ubuntu-20.04           Running         2

5. Open a shell for the Ubuntu sub-system and follow the :ref:`label-install-ubuntu` guide.

.. _label-install-ubuntu:

Install docker into Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
    This guide follows the `official docker documentation <https://docs.docker.com/engine/install/ubuntu/>`_, so have a look into these for more details.

1. Uninstall old versions:

.. code-block:: bash

    $ sudo apt-get remove docker docker-engine docker.io containerd runc

2. Install docker using the repository:

.. code-block:: bash

    $ sudo apt-get update
    $ sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common

3. Add Docker’s official GPG key:

.. code-block:: bash

    $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

4. Use the following command to set up the stable repository:

.. code-block:: bash

    $ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

5. Install the docker engine:

.. code-block:: bash

    $ sudo apt-get update
    $ sudo apt-get install docker-ce docker-ce-cli containerd.io

Potential after-installation steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start the docker daemon manually (if not already started):

.. code-block:: bash

    $ sudo service docker status
    $ sudo service docker start

Add the non-root user to the docker group:

.. code-block:: bash

    $ sudo groupadd docker
    $ sudo usermod -aG docker ${USER}

Re-login.

Verify that you are part of the *docker* group:

.. code-block:: bash

    $ groups $USER

Verify that Docker Engine is installed correctly (should print an informal message and exit):

.. code-block:: bash

    $ docker run hello-world

Checkout slurk
~~~~~~~~~~~~~~~~~~~~~~

.. warning::
    WSL users need to checkout the project using the WSL otherwise the line-endings are not correct!

1. Generate a ssh key pair (with defaults):

.. code-block:: bash

    $ ssh-keygen

2. Upload or copy the generated public key to your `github SSH settings <https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account>`_
3. Clone the repository:

.. code-block:: bash

    $ git clone git@github.com:clp-research/slurk.git

4. Go into the slurk top directory.

Run with docker (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Start the server:

.. code-block:: bash

    $ export SLURK_DOCKER=slurk
    $ scripts/start_server.sh
    b4ad4ccd053bebd4ce80afbeea3a3a259d890ae7103577e003cb2e4b768687fb

2. Fetch the admin token:

.. code-block:: bash

    $ scripts/read_admin_token.sh
    00000000-0000-0000-0000-000000000000

3. (Optional) In case the output of the above script is empty, you may find valuable information in the logs:

.. code-block:: bash

   $ docker logs $SLURK_DOCKER

Run without docker
~~~~~~~~~~~~~~~~~

1. (Optional) Create and activate a virtual environment (with Python 3.9).

    With `Miniconda or Conda <https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html>`_:

    .. code-block:: bash

        $ conda create -n slurk python=3.9
        $ conda activate slurk

    With venv:

    .. code-block:: bash

        $ python3 -m venv slurk
        $ source ./slurk/bin/activate

2. Install dependencies:

    .. code-block:: bash

        $ pip install -r requirements.txt

3. Start the server and get the admin token:

    .. code-block:: bash

        $ scripts/start_server.sh
        [INFO] Starting gunicorn 20.1.0
        [INFO] Listening at: http://0.0.0.0:5000 (1232)
        [INFO] Using worker: geventwebsocket.gunicorn.workers.GeventWebSocketWorker
        [INFO] Booting worker with pid: 1233
        admin token:
        00000000-0000-0000-0000-000000000000


Side-notes
~~~~~~~~~~

The installation of the docker-ce using the WSL showed "failures", but these seem not to have an impact on the docker engine.

.. code-block:: bash

    Setting up docker-ce-cli (5:19.03.13~3-0~ubuntu-focal) ...
    Setting up pigz (2.4-1) ...
    Setting up cgroupfs-mount (1.4) ...
    invoke-rc.d: could not determine current runlevel
    Setting up grub2-common (2.04-1ubuntu26.4) ...
    Setting up grub-pc-bin (2.04-1ubuntu26.4) ...
    Setting up docker-ce (5:19.03.13~3-0~ubuntu-focal) ...
    Created symlink /etc/systemd/system/multi-user.target.wants/docker.service → /lib/systemd/system/docker.service.
    Created symlink /etc/systemd/system/sockets.target.wants/docker.socket → /lib/systemd/system/docker.socket.
    invoke-rc.d: could not determine current runlevel
    Setting up grub-pc (2.04-1ubuntu26.4) ...

    Creating config file /etc/default/grub with new version
    Setting up grub-gfxpayload-lists (0.7) ...
    Processing triggers for install-info (6.7.0.dfsg.2-5) ...
    Processing triggers for libc-bin (2.31-0ubuntu9) ...
    Processing triggers for systemd (245.4-4ubuntu3.2) ...
    Processing triggers for man-db (2.9.1-1) ...
    Processing triggers for linux-image-unsigned-5.6.0-1028-oem (5.6.0-1028.28) ...
    /etc/kernel/postinst.d/initramfs-tools:
    update-initramfs: Generating /boot/initrd.img-5.6.0-1028-oem
    W: mkconf: MD subsystem is not loaded, thus I cannot scan for arrays.
    W: mdadm: failed to auto-generate temporary mdadm.conf file.

This is discussed in the following issue:

.. pull-quote::
    `microsoft/WSL#4903 (mdadm 4.1-2 causes unrecoverable grub config loop in dpkg, apt) <https://github.com/microsoft/WSL/issues/4903>`_
    Spiritually similar #4763 (over there it was LVM). WSL2 does not load the Linux kernel with GRUB (and WSL1 doesn't load a Linux kernel at all). Linux RAID (mdadm) isn't applicable for lack of Multiple Disks. Somehow those were installed on your system. Purging those packages should help.
