from repoze.bfg.view import bfg_view

from bfgsite.interfaces import IWebSite

from bfgsite.utils import API

@bfg_view(for_=IWebSite, name='videos', permission='view',
          renderer='bfgsite.views:templates/videos.pt')
def videos_view(context, request):
    return dict(
        api = API(context, request),
        )

