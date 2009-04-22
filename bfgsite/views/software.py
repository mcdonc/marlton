from repoze.bfg.view import bfg_view
from repoze.bfg.chameleon_zpt import render_template_to_response

from bfgsite.interfaces import IWebSite

from bfgsite.utils import API

@bfg_view(for_=IWebSite, name='software', permission='view')
def software_view(context, request):
    return render_template_to_response(
        'templates/software.pt',
        api = API(context, request),
        )
