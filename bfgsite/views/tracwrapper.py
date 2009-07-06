import lxml.html
from lxml import etree

from BeautifulSoup import BeautifulSoup
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.view import bfg_view

from webob import Response

from bfgsite.interfaces import IWebSite
from bfgsite.utils import API
from bfgsite.utils import get_settings

utf8_html_parser = lxml.html.HTMLParser(encoding='utf-8')

@bfg_view(name='trac', for_=IWebSite, permission='view')
def trac_view(context, request):
    import trac.web.main
    trac_app = trac.web.main.dispatch_request
    from trac.web import HTTPException

    theme = render_template('templates/trac_theme.pt',
                            api=API(context, request))
    settings = get_settings()
    environ = request.environ
    environ['trac.env_path'] = getattr(settings, 'trac.env_path')

    while 1:
        segment = request.path_info_pop()
        if segment == request.view_name:
            break
    try:
        response = request.get_response(trac_app)
    except HTTPException, exc:
        r = Response(str(exc))
        r.status_int = exc.code
        return r

    body_string = response.body

    if (body_string and ('html' in response.content_type
                         or 'xhtml' in response.content_type)):
        theme_bs = BeautifulSoup(theme)
        body_bs = BeautifulSoup(body_string)
        exprs = (
            'metanav',
            'mainnav',
            'main',
            )
        for expr in exprs:
            bodycontent = body_bs.find("div",{'id':expr})
            theme_bs.find("div",{'id':'themecontent'}).append(bodycontent)
        response.body = str(theme_bs)
    return response

