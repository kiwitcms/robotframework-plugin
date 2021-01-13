Robot Framework plugin for Kiwi TCMS
====================================

.. image:: https://img.shields.io/pypi/v/kiwitcms-robotframework-plugin.svg
    :target: https://pypi.org/project/kiwitcms-robotframework-plugin
    :alt: PyPI version

.. image:: https://pyup.io/repos/github/kiwitcms/robotframework-plugin/shield.svg
    :target: https://pyup.io/repos/github/kiwitcms/robotframework-plugin/
    :alt: Python updates

.. image:: https://img.shields.io/badge/kiwi%20tcms-results-9ab451.svg
    :target: https://tcms.kiwitcms.org/plan/290/
    :alt: TP for kiwitcms/robotframework-plugin (master)

.. image:: https://tidelift.com/badges/package/pypi/kiwitcms-robotframework-plugin
    :target: https://tidelift.com/subscription/pkg/pypi-kiwitcms-robotframework-plugin?utm_source=pypi-kiwitcms-robotframework-plugin&utm_medium=github&utm_campaign=readme
    :alt: Tidelift

.. image:: https://img.shields.io/twitter/follow/KiwiTCMS.svg
    :target: https://twitter.com/KiwiTCMS
    :alt: Kiwi TCMS on Twitter

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

- **${plan_id}**: Existing TestPlan ID for storing test execution results.
  **WARNING:** this plugin will create a new TestRun whenever ``plan_id``
  changes! If subsequent test scenarios, aka .robot files don't override
  ``plan_id`` the current one will be used!
- **${product}**: Existing product name when creating a new TestPlan
- **${build_user_email}**: Email for an existing user

.. warning::

    If any of the above variables are missing this plugin will attempt to
    discover the necessary information from your environment. The exect
    behavior is document at
    https://kiwitcms.readthedocs.io/en/latest/plugins/automation-frameworks.html#plugin-configuration

Documentation from test suite(s) is used when creating new TestRun(s).

Each RF test case may also specify the ``TC-xyz`` tag to map to an existing
TestCase in the database. For example::

    *** Settings ***
    Documentation   An example test suite
    Library         OperatingSystem

    *** Variables ***
    ${plan_id}      234

    *** Test Cases ***
    Scenario Maps To Existing TestCase
        [Tags]    TC-607  arbitrary_tag_here
        Should Be Equal    "Hello"    "Hello"

    Hello World Scenario
        [Documentation]    This will be the text of the new TC created in DB
        Should Be Equal    "Hello"    "Hello"

Documentation from test cases is used when creating new TestCase records in
the database.


Usage
-----

::

    robot --listener zealand.listener.KiwiTCMS


Extension and customization
---------------------------

You can customize the behavior of this plugin by extending the listener and
backend classes and overriding some of their methods. For example
save the following in ``acme_tools.py``::

    from zealand.listener import KiwiTCMS
    from zealand.listener import RFBackend


    class JenkinsBackend(RFBackend):
        def get_run_id(self):
            """
                If ${node_name} is specified then tag the TR with "node: X" tag!

                This is done right after a new TR is created!
            """
            run_id = super().get_run_id()

            node_name = self.built_in.get_variable_value('${node_name}')
            if node_name:
                self.rpc.TestRun.add_tag(run_id, 'node: %s' % node_name)
            return run_id

        def finish_test_run(self):
            """
                Do not set TR.stop_date !!!

                If ${jenkins_tag} is specified then tag the TR with it!

                This is executed at the end of each TestRun after all
                execution results have been reported.
            """
            # do not call the inherited method b/c we want to keep these
            # test runs open for inspection by a human !!!
            # super().finish_test_run()

            jenkins_tag = self.built_in.get_variable_value('${jenkins_tag}')
            if jenkins_tag:
                self.rpc.TestRun.add_tag(self.run_id, jenkins_tag)

    class AcmeCorpListener(KiwiTCMS):
        backend_class = JenkinsBackend

        def end_test(self, name, attrs):
            """
                You may also find it more appropriate to override a
                listener class instead.
            """
            super().end_test(name, attrs)

            for tag in attrs['tags']:
                if tag.startswith('JIRA-'):
                    # hyperlink the results between Kiwi TCMS, Jenkins & JIRA
                    # by posting comments everywhere

then instruct Robot Framework to use the overriden listener instead of the
default one::

    robot --listener path/to/acme_tools.py


Changelog
---------

v9.0 (13 Jan 2020)
~~~~~~~~~~~~~~~~~~

- Compatible with Kiwi TCMS v9.0
- Update tcms-api to 9.0


v1.1.0 (28 Oct 2020)
~~~~~~~~~~~~~~~~~~~~

- Update tcms-api to 8.6.0
- Update robotframework to 3.2.2


v1.0.0 (04 May 2020)
~~~~~~~~~~~~~~~~~~~~

- Initial release
- Original implementation by Aniello Barletta
