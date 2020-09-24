.. _slurk_prerequisites:

=========================================
Prerequisites
=========================================

The easiest way to use system is using Docker. For this, ``docker`` is recommended.

- If you are operating on Ubuntu, then follow :ref:`label-install-ubuntu`
- If you are operating on Windows 10, then follow :ref:`label-install-wsl`

For other operating systems, please see the official docker documentation.

.. _label-install-wsl:

Prepare Windows 10
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker cannot easily run on Windows by default. Thus we enable the Windows Subsystem for Linux.
Make sure that Windows 10 has the latest updates installed.

.. note::

    This guide follows the `official WSL2 documentation <https://docs.microsoft.com/de-de/windows/wsl/install-win10>`_, so have a look into these for more details.
    These instructions use experimental features for Docker on Windows and thus could be outdated at any time.
    Furthermore, this guide is a response to a `Problem with getting an admin token (Ubuntu on WSL) <https://github.com/clp-research/slurk/issues/99>`_.

Setting up WSL 2
------------------------------

1. Open a Powershell as Administrator
2. Enable WSL with the following command:

.. code-block:: bash

    $> dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart``

3. Upgrade to WSL2 with the following command:

.. code-block:: bash

    $> dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

4. Set WSL2 as the default for linux distributions:

.. code-block:: bash

    $> wsl --set-default-version 2

5. Restart the system

Install Ubuntu-20.04.1 using the App Store
------------------------------------------

1. After the installation is complete click *Launch*
2. Set a Unix username and password
3. Open a Powershell
4. Check the used WSL version for each distribution using PS:

.. code-block:: bash

    $> wsl --list --verbose
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

    $> sudo apt-get remove docker docker-engine docker.io containerd runc

2. Install docker using the repository:

.. code-block:: bash

    $> sudo apt-get update
    $> sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common

3. Add Docker’s official GPG key:

.. code-block:: bash

    $> curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

4. Use the following command to set up the stable repository.

.. code-block:: bash

    $> sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

5. Install the docker engine

.. code-block:: bash

    $> sudo apt-get update
    $> sudo apt-get install docker-ce docker-ce-cli containerd.io

Potential after-installation steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start the docker deamon manually (if not already started):

.. code-block:: bash

    $> sudo service docker status
    $> sudo service docker start

Add the non-root user to the docker group and re-login:

.. code-block:: bash

    $> sudo groupadd docker
    $> sudo usermod -aG docker ${USER}
    $> su -s ${USER}

Checkout and run slurk
~~~~~~~~~~~~~~~~~~~~~~

.. warning::
    WSL users need to checkout the project using the WSL otherwise the line-endings are not correct!

1. Generate a ssh key pair (with defaults)

.. code-block:: bash

    $> ssh-keygen

2. Upload or copy the generated public key to your github SSH settings
3. Clone the repository

.. code-block:: bash

    $> git clone git@github.com:clp-research/slurk.git

4. Go into the slurk top directory

5. Start the server

.. code-block:: bash

    $> source ./start_slurk_server.sh
    $> echo $SLURK_SERVER_ID
    ce96a2009c0be81f6a82161f611db2f5fd74ed95e8d9b8ea434aeb1bcbb2342b

6. Fetch the admin token

.. code-block:: bash

    $> source ./get_admin_token.sh
    $> echo $ADMIN_TOKEN
    d858f508-da42-4ffb-847c-c7f378c35e02

These commands have to be called with source, because they export environment variables.

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