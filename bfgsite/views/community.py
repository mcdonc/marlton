from repoze.bfg.view import bfg_view
from repoze.bfg.chameleon_zpt import render_template_to_response

from bfgsite.interfaces import IWebSite

from bfgsite.utils import API

@bfg_view(for_=IWebSite, name='community', permission='view')
def community_view(context, request):
    return render_template_to_response(
        'templates/community.pt',
        api = API(context, request),
        )

