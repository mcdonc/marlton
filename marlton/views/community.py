from pyramid.view import view_config

from marlton.interfaces import IWebSite
from marlton.utils import API

@view_config(for_=IWebSite, name='community', permission='view',
             renderer='marlton.views:templates/community.pt')
def community_view(context, request):
    return {'api':API(context, request)}

