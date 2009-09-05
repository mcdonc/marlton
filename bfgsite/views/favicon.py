import os
from webob import Response

from repoze.bfg.view import bfg_view

@bfg_view(name='favicon.ico')
def favicon(context, request):
    response = Response(content_type='image/x-icon')
    here = os.path.dirname(__file__)
    response.body = open(os.path.join(here, 'static',
                                      'images', 'site', 'favicon.ico')).read()
    return response
