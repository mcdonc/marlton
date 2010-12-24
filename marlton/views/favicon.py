import os
from webob import Response

from pyramid.view import bfg_view

_here = os.path.dirname(__file__)
_icon = open(os.path.join(_here, 'static',
                'images', 'site', 'favicon.ico')).read()
_response = Response(content_type='image/x-icon', body=_icon)

@bfg_view(name='favicon.ico')
def favicon_view(context, request):
    return _response
