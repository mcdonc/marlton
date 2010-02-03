from repoze.bfg.view import bfg_view

from bfgsite.interfaces import IWebSite
from bfgsite.utils import API

@bfg_view(for_=IWebSite, name='community', permission='view',
          renderer='bfgsite.views:templates/community.pt')
def community_view(context, request):
    return {'api':API(context, request)}

