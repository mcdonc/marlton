import os
import sys

from paste.deploy import loadapp

from zope.component import getUtility
from repoze.bfg.interfaces import ISettings
from bfgsite.models import SphinxDocument

from repoze.bfg.registry import registry_manager
from repoze.bfg.interfaces import IRootFactory

from bfgsite.catalog import find_catalog

import transaction

def main(argv=sys.argv):
    config = None
    if len(argv) > 1:
        config = sys.argv[1]
    if not config:
        # we assume that the console script lives in the 'bin' dir of a
        # sandbox or buildout, and that the .ini file lives in the 'etc'
        # directory of the sandbox or buildout
        me = sys.argv[0]
        me = os.path.abspath(me)
        sandbox = os.path.dirname(os.path.dirname(me))
        config = os.path.join(sandbox, 'bfgsite.ini')
    exe = sys.executable
    sandbox = os.path.dirname(os.path.dirname(os.path.abspath(exe)))
    app = loadapp('config:%s' % config, name='website')
    registry_manager.push(app.registry)
    root_factory = getUtility(IRootFactory)
    environ = {}
    context = root_factory(environ)
    catalog = find_catalog(context)
    for address in catalog.document_map.address_to_docid:
        if address.startswith('external:'):
            docid = catalog.document_map.address_to_docid[address]
            catalog.unindex_doc(docid)

    settings = getUtility(ISettings)
    docroot = settings.sphinx_docroot
    roots = settings.sphinx_roots
    oldcwd = os.getcwd()

    for root in roots:
        package_dir = roots[root]['package_dir']
        docs_subpath = roots[root]['docs_subpath']
        url_prefix = roots[root]['url_prefix']
        virtual_home = os.path.join(docroot, root)

        os.system('%s/bin/virtualenv --no-site-packages %s' % (
            sys.prefix, virtual_home))
        os.system('%s/bin/easy_install Sphinx' % virtual_home)
        os.system(
            '%s/bin/easy_install repoze.sphinx.autointerface' % virtual_home)

        try:
            os.chdir(package_dir)
            os.system('%s/bin/python setup.py develop' % virtual_home)
        finally:
            os.chdir(oldcwd)

        docs_source = os.path.join(package_dir, docs_subpath)
        os.system(
            '%s/bin/sphinx-build -b html -d %s/doctrees '
            '%s %s/html' % (
            virtual_home, virtual_home, docs_source, virtual_home))
        os.system(
            '%s/bin/sphinx-build -b text -d %s/doctrees '
            '%s %s/text' % (
            virtual_home, virtual_home, docs_source, virtual_home))

        textpath = '%s/text/' % virtual_home

        gen = os.walk(textpath)

        for path, directories, files in gen:
            relpath = path[len(textpath):]
            for filename in files:
                if filename.endswith('.txt'):
                    text = open(os.path.join(path, filename)).read()
                    ob = SphinxDocument(text)
                    filename_no_ext = filename[:-4]
                    path_info = os.path.join(relpath, filename_no_ext)
                    address = 'sphinx:%s/%s.html' % (url_prefix, path_info)
                    docid = catalog.document_map.add(address)
                    catalog.index_doc(docid, ob)
                    data = {'title':filename_no_ext,
                            'type':'Documentation',
                            'text':text}
                    catalog.document_map.add_metadata(docid, data)

        transaction.commit()
        

