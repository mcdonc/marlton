from repoze.bfg.view import bfg_view
from zope.component import queryUtility
from repoze.bfg.interfaces import IDefaultRootFactory
from repoze.bfg.url import route_url

from webob import Response
from bfgsite.interfaces import IWebSite

@bfg_view(for_=IWebSite, route_name='test')
def aview(context, request):
    url = route_url('test', request, can=1, traverse='/a/b/c', bogus=2)
    return Response(url)

def view_factory(environ):
    rf = queryUtility(IDefaultRootFactory)
    root = rf(environ)
    environ['HTTP_X_VHM_ROOT'] = '/tutorialbin'
    return root

    
