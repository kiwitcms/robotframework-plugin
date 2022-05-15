#!/usr/bin/env python
# coding: utf-8
# pylint: disable=missing-docstring
import os
from setuptools import setup


def get_version():
    version_py_path = os.path.join('zealand', 'version.py')
    with open(version_py_path, encoding="utf-8") as version_file:
        version = version_file.read()
        return version.replace(
            ' ', ''
        ).replace('__version__=', '').strip().strip("'").strip('"')


with open("README.rst", encoding="utf-8") as readme:
    LONG_DESCRIPTION = readme.read()


with open('requirements.txt', encoding="utf-8") as requirements_file:
    REQUIREMENTS = requirements_file.readlines()


setup(name='kiwitcms-robotframework-plugin',
      version=get_version(),
      packages=['zealand'],
      description='robotframework integration with kiwi TCMS',
      long_description=LONG_DESCRIPTION,
      long_description_content_type="text/x-rst",
      author='Aniello Barletta',
      author_email='aniellob@gmail.com',
      maintainer='Kiwi TCMS',
      maintainer_email='info@kiwitcms.org',
      url='https://github.com/kiwitcms/robotframework-plugin',
      license='GPLv3+',
      install_requires=REQUIREMENTS,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3' +
          ' or later (GPLv3+)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
      ])
