from repoze.bfg.view import bfg_view

from bfgsite.interfaces import IWebSite

from bfgsite.utils import API

@bfg_view(for_=IWebSite, name='software', permission='view',
          renderer='bfgsite.views:templates/software.pt')
def software_view(context, request):
    return dict(
        api = API(context, request),
        )

