from repoze.zodbconn.finder import PersistentApplicationFinder
from repoze.bfg.router import make_app as bfg_make_app
from bfgsite.models import appmaker

def make_app(global_config, **kw):
    # paster app config callback
    zodb_uri = kw.get('zodb_uri', None)
    if zodb_uri is None:
        raise ValueError('zodb_uri must not be None')        
    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    import bfgsite
    app = bfg_make_app(finder, bfgsite, options=kw)
    return app

