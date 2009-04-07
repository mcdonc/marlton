def make_app(global_config, **kw):
    # paster app config callback
    from repoze.bfg.router import make_app
    from bfgsite.models import appmaker
    db_path = kw.get('db_path', None)
    if db_path is None:
        raise ValueError('db_path must not be None')        
    from repoze.zodbconn.finder import PersistentApplicationFinder
    finder = PersistentApplicationFinder('file://%s' % db_path, appmaker)
    import bfgsite
    app = make_app(finder, bfgsite, options=kw)
    return app

if __name__ == '__main__':
    from paste import httpserver
    app = make_app(None)
    httpserver.serve(app, host='0.0.0.0', port='5432')
    
