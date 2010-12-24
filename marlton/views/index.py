from webob import Response

from pyramid.view import view_config

from marlton.interfaces import IWebSite

from marlton.utils import API
from marlton.utils import get_tutorials

@view_config(for_=IWebSite, permission='view',
             renderer='marlton.views:templates/index.pt')
def index_view(context, request):
    tutorials = get_tutorials(context['tutorialbin'], request, 5)
    return {'api' :API(context, request), 'tutorials':tutorials}

@view_config(for_=IWebSite, name='robots.txt')
def robots_txt(context, request):
    response  = Response('User-Agent: * \nDisallow: /trac/',
                         content_type='text/plain')
    return response

                    
