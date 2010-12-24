from pyramid.view import view_config

from marlton.interfaces import IWebSite

from marlton.utils import API

@view_config(for_=IWebSite, name='documentation', permission='view',
             renderer='marlton.views:templates/documentation.pt')
def docs_view(context, request):
    return {'api':API(context, request)}

