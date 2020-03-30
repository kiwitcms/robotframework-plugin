#!/usr/bin/env python
# coding: utf-8
# pylint: disable=missing-docstring
from setuptools import setup
import sys


with open("README.rst") as readme:
    LONG_DESCRIPTION = readme.read()


setup(name='zealand',
      version='1.0.4',
      packages=['zealand', 'zealand.tcms_api'],
      description='robotframework integration with kiwi TCMS',
      long_description=LONG_DESCRIPTION,
      maintainer='Aniello Barletta',
      maintainer_email='aniellob@gmail.com',
      license='LGPLv2+',
      url='https://github.com/shadeimi/zealand',
      python_requires='>=3.6',
          install_requires=[] + (
        ["winkerberos"] if sys.platform.startswith("win") else ["kerberos"]
        ),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU Lesser General Public License v2' +
          ' or later (LGPLv2+)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
      ])
