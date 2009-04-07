import os
import sys
import urlparse

import formencode
import webob

from paste import urlparser

import pygments
from pygments import lexers
from pygments import formatters
from pygments import util

from repoze.bfg.wsgi import wsgiapp
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.traversal import find_interface
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.monty import marshal

from bfgsite.models import PasteEntry
from bfgsite.models import IPasteBin
from bfgsite.website import preferred_author
from bfgsite.website import COOKIE_AUTHOR
from bfgsite.website import COOKIE_LANGUAGE
from bfgsite.utils import sort_byint

def get_pastes(context, request, max):
    pastebin = find_interface(context, IPasteBin)
    pastes = []
    pastebin_url = model_url(pastebin, request)
    keys = sort_byint(pastebin.keys())
    keys = keys[:max]
    for name in keys:
        entry = pastebin[name]
        if entry.date is not None:
            pdate = entry.date.strftime('%x')
        else:
            pdate = 'UNKNOWN'
        paste_url = urlparse.urljoin(pastebin_url, name)
        new = {'author':entry.author_name, 'date':pdate, 'url':paste_url,
               'language':entry.language,'name':name}
        pastes.append(new)
    return pastes

formatter = formatters.HtmlFormatter(linenos=True,
                                     cssclass="source")
style_defs = formatter.get_style_defs()

def entry_view(context, request):
    paste = context.paste or u''
    try:
        if context.language:
            l = lexers.get_lexer_by_name(context.language)
        else:
            l = lexers.guess_lexer(context.paste)
        language = l.aliases[0]
    except util.ClassNotFound, err:
        # couldn't guess lexer
        l = lexers.TextLexer()

    formatted_paste = pygments.highlight(paste, l, formatter)
    pastes = get_pastes(context, request, 10)

    return render_template_to_response(
        'templates/entry.pt',
        author = context.author_name,
        date = context.date.strftime('%x at %X'),
        style_defs = style_defs,
        lexer_name = l.name,
        paste = formatted_paste,
        pastes = pastes,
        message = None,
        application_url = request.application_url,
        pastebin_url = model_url(context.__parent__, request)
        )

all_lexers = list(lexers.get_all_lexers())
all_lexers.sort()
lexer_info = []
for name, aliases, filetypes, mimetypes_ in all_lexers:
    lexer_info.append({'alias':aliases[0], 'name':name})

class PasteAddSchema(formencode.Schema):
    allow_extra_fields = True
    paste = formencode.validators.NotEmpty()

def pastebin_view(context, request):
    params = request.params
    author_name = preferred_author(request)
    language = u''
    paste = u''
    message = u''
    response = webob.Response()
    app_url = request.application_url
    pastebin_url = model_url(context, request)
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)

    if params.has_key('form.submitted'):
        paste = request.params.get('paste', '')
        author_name = request.params.get('author_name', '')
        language = request.params.get('language', '')
        schema = PasteAddSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            response.set_cookie(COOKIE_AUTHOR, author_name)
            response.set_cookie(COOKIE_LANGUAGE, language)

            if isinstance(author_name, str):
                author_name = unicode(author_name, 'utf-8')
            if isinstance(language, str):
                language = unicode(language, 'utf-8')
            if isinstance(paste, str):
                paste = unicode(paste, 'utf-8')

            pobj = PasteEntry(author_name, paste, language)
            pasteid = context.add(pobj)
            response.status = '301 Moved Permanently'
            response.headers['Location'] = '%s%s' % (pastebin_url, pasteid)

    pastes = get_pastes(context, request, 10)

    body = render_template(
        'templates/pastebin.pt',
        author_name = author_name,
        paste = paste,
        lexers = lexer_info,
        message = message,
        pastes = pastes,
        application_url = app_url,
        pastebin_url = pastebin_url,
        user = user,
        can_manage = can_manage,
        )
    response.unicode_body = unicode(body)
    return response

def pastebin_manage_view(context, request):
    params = request.params
    message = u''
    response = webob.Response()
    app_url = request.application_url
    pastebin_url = model_url(context, request)

    if params.has_key('form.submitted'):
        form = marshal(request.environ, request.body_file)
        checkboxes = form.get('delete', [])
        for checkbox in checkboxes:
            del context[checkbox]
        message = '%s pastes deleted' % len(checkboxes)
        response.status = '301 Moved Permanently'
        response.headers['Location'] = pastebin_url

    pastes = get_pastes(context, request, sys.maxint)

    body = render_template(
        'templates/pastebin_manage.pt',
        pastes = pastes,
        application_url = app_url,
        pastebin_url = pastebin_url,
        )
    response.unicode_body = unicode(body)
    return response
        
def pastebin_rss_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    pastebin_url = model_url(context, request)
    pastes = get_pastes(context, request, sys.maxint)
    if pastes:
        last_date=pastes[0]['date']
    else:
        last_date=None
    body = render_template(
        'templates/pastebin_rss.pt',
        pastes = pastes,
        last_date = last_date,
        application_url = app_url,
        pastebin_url = pastebin_url,
        )
    response.unicode_body = unicode(body)
    return response    
