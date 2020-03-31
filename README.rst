Robot Framework plugin for Kiwi TCMS
====================================

This package allows you execute your *Robot Framework* test suite and report the
results into `Kiwi TCMS <http://kiwitcms.org>`_.

Installation
------------

::

    pip install kiwitcms-robotframework-plugin


Configuration and environment
-----------------------------

Minimal config file `~/.tcms.conf`::

    [tcms]
    url = https://tcms.server/xml-rpc/
    username = your-username
    password = your-password


For more info see `tcms-api docs <https://tcms-api.readthedocs.io>`_.


Usage
-----

::

    robot --listener zealand.zealandListener.py
