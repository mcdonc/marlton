from webob import Response

from pyramid.chameleon_zpt import render_template
from pyramid.url import model_url

from marlton.utils import find_site
from marlton.utils import API

def forbidden(context, request):
    site = find_site(context)
    environ = request.environ
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
        response = Response(body, headers=headerlist, status='403 Forbidden')
    elif 'login' in referrer:
        # this request came from a user submitting the login form
        login_url = model_url(site, request, 'login',
                              query={'reason':'Bad username or password',
                                     'came_from':request.url})
        headerlist = [('Location', login_url)]
        response = Response('', headers=headerlist, status='403 Forbidden')
    else:
        # the user is not authenticated and did not come in as a result of
        # submitting the login form
        query = {'came_from':request.url}
        url = request.url
        while url.endswith('/'):
            url = url[:-1]
        if url != request.application_url: # if request isnt for homepage
            query['reason'] = 'Not logged in'
        login_url = model_url(site, request, 'login', query=query)
        headerlist = [('Location', login_url)]
        response = Response('', headers=headerlist, status='302 Found')
    return response


