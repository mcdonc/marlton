from pyramid.view import bfg_view

from marlton.interfaces import IWebSite
from marlton.utils import API

@bfg_view(for_=IWebSite, name='community', permission='view',
          renderer='marlton.views:templates/community.pt')
def community_view(context, request):
    return {'api':API(context, request)}

