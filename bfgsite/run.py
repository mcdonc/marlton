from repoze.zodbconn.finder import PersistentApplicationFinder
from repoze.bfg.router import make_app as bfg_make_app
from repoze.bfg.authentication import AuthTktAuthenticationPolicy
from repoze.bfg.threadlocal import get_current_request

from bfgsite.models import appmaker
from bfgsite.utils import find_users
from bfgsite.utils import find_profiles

def make_app(global_config, **kw):
    # paster app config callback
    zodb_uri = kw.get('zodb_uri', None)
    if zodb_uri is None:
        raise ValueError('zodb_uri must not be None')        

    roots = {}
    for k in kw:
        if k.startswith('sphinx.'):
            prefix, rest = k.split('sphinx.', 1)
            name, setting = rest.split('.', 1)
            settings = roots.setdefault(name, {})
            settings[setting] = kw[k]

    kw['sphinx_roots'] = roots

    for rootname, settings in roots.items():
        if not 'url_prefix' in settings:
            raise ValueError('sphinx.%s.url_prefix missing' % rootname)
        if not 'package_dir' in settings:
            raise ValueError('sphinx.%s.package_dir missing' % rootname)
        if not 'docs_subpath' in settings:
            raise ValueError('sphinx.%s.docs_subpath missing' % rootname)
        if not 'title' in settings:
            raise ValueError('sphinx.%s.title missing' % rootname)
        if not 'description' in settings:
            settings['description'] = rootname

    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def groupfinder(userid, request=None):
        environ = {}
        if request is None:
            request = get_current_request()
        else:
            root = request.root
            environ = request.environ
        users = find_users(root)
        info = users.get_by_id(userid)
        if info:
            groups = info['groups']
            environ['REMOTE_ID'] = userid
            environ['REMOTE_USER'] = info['login']
            environ['REMOTE_GROUPS'] = groups
            profiles = find_profiles(root)
            profile = profiles.get(userid)
            if profile:
                environ['REMOTE_EMAIL'] = profile.email
            return groups
    policy = AuthTktAuthenticationPolicy('sosecret', callback=groupfinder)
    import bfgsite
    app = bfg_make_app(finder, bfgsite, authentication_policy=policy,options=kw)
    return app

