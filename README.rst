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

Each RF suite may define the following variables:

- **${plan_id}**: Existing TestPlan ID
- **${product}**: Existing product name
- **${build_user_email}**: Email for an existing user
- **${node_name}**: ....

.. warning::

    If any of the above variables are missing this plugin will attempt to
    discover the necessary information from your environment. The exect
    behavior is document at
    https://kiwitcms.readthedocs.io/en/latest/plugins/automation-frameworks.html#plugin-configuration


Usage
-----

::

    robot --listener zealand.listener.KiwiTCMS
