import os
from webob import Response

from repoze.bfg.view import bfg_view

_here = os.path.dirname(__file__)
_icon = open(os.path.join(_here, 'static',
                'images', 'site', 'favicon.ico')).read()

@bfg_view(name='favicon.ico')
def favicon(context, request):
    return Response(content_type='image/x-icon', body=_icon)
