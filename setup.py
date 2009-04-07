##############################################################################
#
# Copyright (c) 2009 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'repoze.bfg',
    'repoze.tm2',
    'repoze.monty',
    'repoze.who',
    'ZODB3',
    'Pygments',
    'FormEncode',
    'zope.security',
    'nose',
    'repoze.zodbconn',
    ]

def get_version():
    try:
        here = os.path.abspath(os.path.dirname(__file__))
    except NameError:
        here = os.path.abspath(os.getcwd())
    f = os.path.join(here, 'bfgsite', 'VERSION.txt')
    version = open(f).readline().strip()
    return version

setup(name='bfgsite',
      version=get_version(),
      description='A web site for repoze.bfg with a paste bin and a tutorial bin',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      keywords='paste bin tutorial cluebin repoze bfg wsgi website',
      author="Carlos de la Guardia",
      author_email="cguardia@yahoo.com",
      url="http://www.delaguardia.com.mx",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=[],
      zip_safe=False,
      tests_require = requires,
      install_requires= requires,
      test_suite="nose.collector",
      entry_points = """\
      [paste.app_factory]
      make_app = bfgsite.run:make_app
      """
      )

