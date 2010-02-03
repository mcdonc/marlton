from webob import Response

from repoze.bfg.view import bfg_view

from bfgsite.interfaces import IWebSite

from bfgsite.utils import API
from bfgsite.utils import get_tutorials

@bfg_view(for_=IWebSite, permission='view',
          renderer='bfgsite.views:templates/index.pt')
def index_view(context, request):
    tutorials = get_tutorials(context['tutorialbin'], request, 5)
    return {'api' :API(context, request), 'tutorials':tutorials}

@bfg_view(for_=IWebSite, name='robots.txt')
def robots_txt(context, request):
    response  = Response('User-Agent: * \nDisallow: /trac/',
                         content_type='text/plain')
    return response

                    
