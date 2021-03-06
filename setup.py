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

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'repoze.tm2',
    'repoze.monty',
    'repoze.who',
    'repoze.whoplugins.zodb',
    'repoze.retry',
    'ZODB3',
    'Pygments',
    'FormEncode',
    'nose',
    'repoze.zodbconn',
    'repoze.folder',
    'PyCAPTCHA',
    'Pillow',
    'repoze.session',
    'repoze.browserid',
    'repoze.catalog',
    'repoze.lemonade',
    'virtualenv',
    'Sphinx',
    'repoze.sphinx.autointerface',
    'repoze.sendmail',
    'docutils',
    ]

setup(name='marlton',
      version='0.0',
      description=('A web site for Pyramid with a paste bin and a tutorial '
                   'bin'),
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      keywords='paste bin tutorial pyramid wsgi website',
      author="Carlos de la Guardia, Chris McDonough",
      author_email="cguardia@yahoo.com",
      url="http://www.delaguardia.com.mx",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      dependency_links = [
          'http://dist.repoze.org/bfgsite/PyCAPTCHA-0.4repoze2.tar.gz'],
      include_package_data=True,
      zip_safe=False,
      tests_require = requires,
      install_requires= requires,
      test_suite="nose.collector",
      entry_points = """\
      [paste.app_factory]
      main = marlton:main

      [console_scripts]
      reindex_sphinx_docs = marlton.scripts.reindex_sphinx_docs:main
      debug_marlton = marlton.scripts.debug:main
      """
      )

