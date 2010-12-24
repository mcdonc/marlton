from pyramid.threadlocal import get_current_request
from marlton.utils import find_users
from marlton.utils import find_profiles

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
