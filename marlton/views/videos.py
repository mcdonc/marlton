from pyramid.view import bfg_view

from marlton.interfaces import IWebSite

from marlton.utils import API

@bfg_view(for_=IWebSite, name='videos', permission='view',
          renderer='marlton.views:templates/videos.pt')
def videos_view(context, request):
    return dict(
        api = API(context, request),
        )

for x in range(1, 11):
    # add groundhog1 - 10 urls
    gh_view = bfg_view(for_=IWebSite, name='groundhog%s' % x, permission='view',
                       renderer='marlton.views:templates/videos.pt')
    videos_view = gh_view(videos_view)
