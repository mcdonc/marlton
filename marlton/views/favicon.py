import os
from webob import Response

from pyramid.view import view_config

_here = os.path.dirname(__file__)
_icon = open(os.path.join(_here, 'static',
                'images', 'site', 'favicon.ico')).read()
_response = Response(content_type='image/x-icon', body=_icon)

@view_config(name='favicon.ico')
def favicon_view(context, request):
    return _response
