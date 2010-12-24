import lxml.html
from lxml import etree

from pyramid.chameleon_zpt import render_template
from pyramid.view import bfg_view
from pyramid.settings import get_settings

from webob import Response

from marlton.interfaces import IWebSite
from marlton.utils import API

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
        # assumes trac returns utf-8 responses (not the default)
        parser = utf8_html_parser
        theme_lxml = lxml.html.document_fromstring(theme, parser=parser)
        body_lxml = lxml.html.document_fromstring(body_string, parser=parser)
        themecontent = theme_lxml.xpath('//div[@id="themecontent"]')
        exprs = (
#            '//div[@id="metanav"]', # this is the login and preferences links
            '//div[@id="mainnav"]',
            '//div[@id="main"]'
            )
        for expr in exprs:
            bodycontent = body_lxml.xpath(expr)
            themecontent[0].append(bodycontent[0])
        body = etree.tostring(theme_lxml)
        response.body = STRICT + '\n' + body
    return response

STRICT = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">"""
