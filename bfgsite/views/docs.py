from repoze.bfg.view import bfg_view

from bfgsite.interfaces import IWebSite

from bfgsite.utils import API

@bfg_view(for_=IWebSite, name='documentation', permission='view',
          renderer='bfgsite.views:templates/documentation.pt')
def docs_view(context, request):
    return {'api':API(context, request)}

