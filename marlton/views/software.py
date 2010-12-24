from pyramid.view import bfg_view

from marlton.interfaces import IWebSite

from marlton.utils import API

@bfg_view(for_=IWebSite, name='software', permission='view',
          renderer='marlton.views:templates/software.pt')
def software_view(context, request):
    return dict(
        api = API(context, request),
        )

