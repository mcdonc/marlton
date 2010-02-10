from repoze.zodbconn.finder import PersistentApplicationFinder
from repoze.bfg.configuration import Configurator

from bfgsite.models import appmaker

def make_app(global_config, **settings):
    # paster app config callback
    zodb_uri = settings.get('zodb_uri', None)
    if zodb_uri is None:
        raise ValueError('zodb_uri must not be None')        

    roots = {}

    for k in settings:
        if k.startswith('sphinx.'):
            prefix, rest = k.split('sphinx.', 1)
            name, setting = rest.split('.', 1)
            tmp = roots.setdefault(name, {})
            tmp[setting] = settings[k]

    settings['sphinx_roots'] = roots

    for rootname, tmp in roots.items():
        if not 'url_prefix' in tmp:
            raise ValueError('sphinx.%s.url_prefix missing' % rootname)
        if not 'package_dir' in tmp:
            raise ValueError('sphinx.%s.package_dir missing' % rootname)
        if not 'docs_subpath' in tmp:
            raise ValueError('sphinx.%s.docs_subpath missing' % rootname)
        if not 'title' in tmp:
            raise ValueError('sphinx.%s.title missing' % rootname)
        if not 'description' in tmp:
            tmp['description'] = rootname

    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    config = Configurator(settings=settings, root_factory=finder)
    config.begin()
    config.load_zcml('configure.zcml')
    config.end()
    config.hook_zca()
    app = config.make_wsgi_app()
    return app

