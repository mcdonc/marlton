import sys

from webob.exc import HTTPFound

import formencode

from pygments import lexers
from pygments import util
from pygments import highlight


from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.bfg.view import bfg_view

from repoze.monty import marshal

from bfgsite.interfaces import IPasteBin
from bfgsite.interfaces import IPasteEntry

from bfgsite.models import PasteEntry

from bfgsite.utils import API
from bfgsite.utils import COOKIE_AUTHOR
from bfgsite.utils import COOKIE_LANGUAGE
from bfgsite.utils import formatter
from bfgsite.utils import get_pastes
from bfgsite.utils import preferred_author
from bfgsite.utils import lexer_info
from bfgsite.utils import nl_to_br
from bfgsite.utils import style_defs

@bfg_view(for_=IPasteEntry, permission='view')
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

    formatted_paste = highlight(paste, l, formatter)
    pastes = get_pastes(context, request, 10)

    return render_template_to_response(
        'templates/paste_entry.pt',
        api = API(context, request),
        author = context.author_name,
        date = context.date.strftime('%x at %X'),
        style_defs = style_defs,
        lexer_name = l.name,
        paste = formatted_paste,
        pastes = pastes,
        message = None,
        pastebin_url = model_url(context.__parent__, request)
        )

@bfg_view(for_=IPasteBin, permission='view')
def pastebin_view(context, request):
    params = request.params
    author_name = preferred_author(context, request)
    language = u''
    paste = u''
    message = u''
    pastebin_url = model_url(context, request)
    can_manage = has_permission('manage', context, request)

    if params.has_key('form.submitted'):
        paste = params.get('paste', '')
        author_name = params.get('author_name', '')
        language = params.get('language', '')
        schema = PasteAddSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            pobj = PasteEntry(author_name, paste, language)
            pasteid = context.add(pobj)
            url = '%s%s' % (pastebin_url, pasteid)
            response = HTTPFound(location=url)
            response.set_cookie(COOKIE_AUTHOR, author_name, max_age=864000)
            response.set_cookie(COOKIE_LANGUAGE, language)
            return response

    pastes = get_pastes(context, request, 10)

    return render_template_to_response(
        'templates/pastebin.pt',
        api = API(context, request),
        author_name = author_name,
        paste = paste,
        lexers = lexer_info,
        message = message,
        pastes = pastes,
        pastebin_url = pastebin_url,
        can_manage = can_manage,
        manage_url = model_url(context, request, 'manage'),
        )
    
@bfg_view(for_=IPasteBin, name='manage', permission='manage')
def pastebin_manage_view(context, request):
    params = request.params
    message = params.get('message', u'')

    if params.has_key('form.submitted'):
        form = marshal(request.environ, request.body_file)
        checkboxes = form.get('delete', [])
        for checkbox in checkboxes:
            del context[checkbox]
        message = '%s pastes deleted' % len(checkboxes)
        url = model_url(context, request, 'manage', query={'message':message})
        response = HTTPFound(location=url)
        response.headers['Location'] = url
        return response

    pastebin_url = model_url(context, request)
    pastes = get_pastes(context, request, sys.maxint)

    return render_template_to_response(
        'templates/pastebin_manage.pt',
        api = API(context, request),
        pastes = pastes,
        message = message,
        pastebin_url = pastebin_url,
        )
        
@bfg_view(for_=IPasteBin, name='rss', permission='view')
def pastebin_rss_view(context, request):
    pastebin_url = model_url(context, request)
    pastes = get_pastes(context, request, sys.maxint)
    if pastes:
        last_date=pastes[0]['date']
    else:
        last_date=None
    for paste in pastes:
        paste['body'] = nl_to_br(paste['body'])
    response = render_template_to_response(
        'templates/pastebin_rss.pt',
        pastes = pastes,
        last_date = last_date,
        pastebin_url = pastebin_url,
        )
    response.content_type = 'application/rss+xml'
    return response

class PasteAddSchema(formencode.Schema):
    allow_extra_fields = True
    paste = formencode.validators.NotEmpty()


