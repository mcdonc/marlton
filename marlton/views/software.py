from pyramid.view import view_config

from marlton.interfaces import IWebSite

from marlton.utils import API

@view_config(for_=IWebSite, name='software', permission='view',
             renderer='marlton.views:templates/software.pt')
def software_view(context, request):
    return dict(
        api = API(context, request),
        )

