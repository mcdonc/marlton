from webob.exc import HTTPFound

from pyramid.security import forget
from pyramid.security import remember
from pyramid.security import authenticated_userid
from pyramid.view import bfg_view
from pyramid.url import model_url

from repoze.who.plugins.zodb.users import get_sha_password

from marlton.interfaces import IWebSite
from marlton.utils import API
from marlton.utils import find_users

@bfg_view(for_=IWebSite, name='logout', permission='view')
def logout_view(context, request):
    headers = forget(request)
    return HTTPFound(location=model_url(context, request), headers=headers)

@bfg_view(for_=IWebSite, name='login', permission='view',
          renderer='marlton.views:templates/login.pt')
def login_view(context, request):
    login = ''
    password = ''
    came_from = request.params.get('came_from')
    message = request.params.get('reason')
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        users = find_users(context)
        info = users.get_by_login(login)
        if info:
            if info['password'] == get_sha_password(password):
                headers = remember(request, info['id'])
                if came_from:
                    return HTTPFound(location=came_from, headers=headers)
                else:
                    url = model_url(context, request, 'login')
                    return HTTPFound(location=url, headers=headers)
            else:
                message = 'Wrong password'
        else:
            message = 'No such user name %s' % login

    logged_in = authenticated_userid(request)
        
    return dict(
        api = API(context, request),
        login = login,
        password = password,
        logged_in = logged_in,
        came_from = came_from,
        message = message,
        )

