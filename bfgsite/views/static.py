import os

from repoze.bfg.view import static

from bfgsite.interfaces import IWebSite

from repoze.bfg.view import bfg_view

static_dir = os.path.join(os.path.dirname(__file__), 'static')
static_app = static(static_dir)

@bfg_view(for_=IWebSite, name='static', permission='view')
def static_view(context, request):
    return static_app(context, request)

