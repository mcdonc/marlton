from repoze.bfg.security import ACLSecurityPolicy

from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin

from zope.interface import classProvides
from paste.request import construct_url

from webob import Request

from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.url import model_url
from repoze.bfg.interfaces import IUnauthorizedAppFactory

from bfgsite.utils import find_users
from bfgsite.utils import find_profiles
from bfgsite.utils import find_site
from bfgsite.utils import API

class StandaloneSecurityPolicy(ACLSecurityPolicy):
    def __init__(self):
        self.auth = AuthTktCookiePlugin('sosecret')

    def get_principals(self, request):
        # self.permits must have been called first (an invariant when
        # running under bfg, as .permits is called at ingress before
        # anything else)
        user_id = request.environ.get('REMOTE_ID')
        principals = []
        if user_id:
            principals.append(user_id)
            group_ids = request.environ.get('REMOTE_GROUPS')
            if group_ids:
                principals.extend(group_ids)
        return principals

    def permits(self, context, request, permission):
        identity = self.auth.identify(request.environ)
        if identity is not None:
            userid = identity.get('repoze.who.userid')
            if userid is not None:
                users = find_users(context)
                info = users.get_by_id(userid)
                if info:
                    profiles = find_profiles(context)
                    profile = profiles.get(userid)
                    request.environ['REMOTE_ID'] = userid
                    request.environ['REMOTE_USER'] = info['login']
                    request.environ['REMOTE_GROUPS'] = info['groups']
                    if profile:
                        request.environ['REMOTE_EMAIL'] = profile.email
        return ACLSecurityPolicy.permits(self, context, request, permission)

def BFGSiteSecurityPolicy():
    return StandaloneSecurityPolicy()

class Forbidden:
    classProvides(IUnauthorizedAppFactory)
    def __call__(self, environ, start_response):
        request = Request(environ=environ)
        context = request.context
        site = find_site(context)
        referrer = environ.get('HTTP_REFERER', '')
        if 'REMOTE_ID' in environ:
            # the user is authenticated but he is not allowed to access this
            # resource
            api = API(context, request)
            body =  render_template(
                'templates/forbidden.pt',
                api=api,
                login_form_url = model_url(site, request, 'login'),
                homepage_url = model_url(site, request),
                )
            headerlist = []
            headerlist.append(('Content-Type', 'text/html; charset=utf-8'))
            headerlist.append(('Content-Length', str(len(body))))
            start_response('403 Forbidden', headerlist)
            return [body]
        elif 'login' in referrer:
            # this request came from a user submitting the login form
            login_url = model_url(site, request, 'login',
                                  query={'reason':'Bad username or password',
                                         'came_from':construct_url(environ)})
            start_response('302 Found', [('Location', login_url)])
            return ''
        else:
            # the user is not authenticated and did not come in as a result of
            # submitting the login form
            query = {'came_from':construct_url(environ)}
            url = request.url
            while url.endswith('/'):
                url = url[:-1]
            if url != request.application_url: # if request isnt for homepage
                query['reason'] = 'Not logged in'
            login_url = model_url(site, request, 'login', query=query)
            start_response('302 Found', [('Location', login_url)])
            return ''


