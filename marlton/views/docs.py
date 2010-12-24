from pyramid.view import bfg_view

from marlton.interfaces import IWebSite

from marlton.utils import API

@bfg_view(for_=IWebSite, name='documentation', permission='view',
          renderer='marlton.views:templates/documentation.pt')
def docs_view(context, request):
    return {'api':API(context, request)}

