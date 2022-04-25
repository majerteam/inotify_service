Inotify service
=================

inotify_service can be used to build a Linux service similar to the outdated incron.

It's based on the (simple and efficient) python asyncinotify package.

We (Majerti) use it in production with a low load. We don't have any feedback on performance to provide.

Install
----------

.. code-block:: command

    apt-get install python3-venv
    python3 -m venv /usr/local/inotify_service_venv
    source /usr/local/inotify_service_venv/bin/activate

Setup
-------

You can download a suitable log.conf sample file on the github page :

https://github.com/majerteam/inotify_service/


.. code-block:: command

    mkdir -p /etc/inotify_service/conf.d
    cp log.conf /etc/inotify_service/


Add yaml configuration files for the directories you want to watch.

Each yaml file can contain one or more configurations placed into a yaml list

.. code-block:: yaml

    - script: "sleep 2 | echo {path} > /tmp/titi.log"
      directory: "/tmp"
      pattern: "[a-z0-9_]+\\.pdf$"
      events:
        - "CLOSE_WRITE"
        - "MOVED_TO"

    - script: "echo {path}"
      directory: "/home/gas/tmp/"
      events:
        - "CLOSE_WRITE"


Mandatory parameters:

*script* : The command to launch, the following parameters are passed

- path : The absolute path on disk
- name : The event name (CLOSE_WRITE ...)

*directory* : The directory to watch

*events* : List of events that should fire the script

Optionnal parameters:

*pattern* : A regexp pattern used to match the file names that can be managed


Systemd Service Setup
------------------------

If you used the same directories as here above you can just use the .service file that you can download in the github repository.

https://github.com/majerteam/inotify_service/

.. code-block:: command

    cp inotify_service.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable inotify_service.service
    systemctl start inotify_service.service
    systemctl status inotify_service.service  # Default configuration should print the directories that are watched