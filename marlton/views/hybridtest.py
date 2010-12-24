from pyramid.view import bfg_view
from zope.component import queryUtility
from pyramid.interfaces import IDefaultRootFactory
from pyramid.url import route_url

from webob import Response
from marlton.interfaces import IWebSite

@bfg_view(for_=IWebSite, route_name='test')
def aview(context, request):
    url = route_url('test', request, can=1, traverse='/a/b/c', bogus=2)
    return Response(url)

def view_factory(environ):
    rf = queryUtility(IDefaultRootFactory)
    root = rf(environ)
    environ['HTTP_X_VHM_ROOT'] = '/tutorialbin'
    return root

    
