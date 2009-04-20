from repoze.bfg.security import ACLSecurityPolicy

from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin

from bfgsite.utils import find_users
from bfgsite.utils import find_profiles

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

