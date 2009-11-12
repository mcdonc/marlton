from webob import Response

from repoze.bfg.view import bfg_view
from repoze.bfg.chameleon_zpt import render_template_to_response

from bfgsite.interfaces import IWebSite

from bfgsite.utils import API
from bfgsite.utils import get_tutorials

@bfg_view(for_=IWebSite, permission='view')
def index_view(context, request):
    tutorials = get_tutorials(context['tutorialbin'], request, 5)
    return render_template_to_response(
        'templates/index.pt',
        api = API(context, request),
        tutorials = tutorials,
        )

@bfg_view(for_=IWebSite, name='robots.txt', permission='view')
def robots_txt(context, request):
    response  = Response('User-Agent: * \nDisallow: /trac/')
    response.content_type = 'text/plain'
    return response

                    
