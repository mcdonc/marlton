import sys

from webob.exc import HTTPFound

import formencode

from pygments import lexers
from pygments import util
from pygments import highlight

from pyramid.security import has_permission
from pyramid.url import resource_url
from pyramid.view import view_config

from repoze.monty import marshal

from marlton.interfaces import IPasteBin
from marlton.interfaces import IPasteEntry

from marlton.models import PasteEntry
from marlton import utils

@view_config(for_=IPasteEntry, permission='view',
             renderer='marlton.views:templates/paste_entry.pt')
def entry_view(context, request):
    paste = context.paste or u''
    try:
        if context.language:
            l = lexers.get_lexer_by_name(context.language)
        else:
            l = lexers.guess_lexer(context.paste)
    except util.ClassNotFound:
        # couldn't guess lexer
        l = lexers.TextLexer()

    formatted_paste = highlight(paste, l, utils.formatter)
    pastes = utils.get_pastes(context, request, 10)

    return dict(
        api = utils.API(context, request),
        author = context.author_name,
        date = context.date.strftime('%x at %X'),
        style_defs = utils.style_defs,
        lexer_name = l.name,
        paste = formatted_paste,
        pastes = pastes,
        message = None,
        pastebin_url = resource_url(context.__parent__, request)
        )

@view_config(for_=IPasteBin, permission='view',
             renderer='marlton.views:templates/pastebin.pt')
def pastebin_view(context, request):
    params = request.params
    author_name = utils.preferred_author(context, request)
    language = u''
    paste = u''
    message = u''
    pastebin_url = resource_url(context, request)
    can_manage = has_permission('manage', context, request)

    if params.has_key('form.submitted'):
        if params.get('text'): # trap spambots
            return HTTPFound(location=resource_url(context, request))
        paste = params.get('paste_', '')
        author_name = params.get('author_name_', '')
        language = params.get('language_', '')
        schema = PasteAddSchema()
        message = None
        try:
            schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            pobj = PasteEntry(author_name, paste, language)
            pasteid = context.add_item(pobj)
            url = '%s%s' % (pastebin_url, pasteid)
            response = HTTPFound(location=url)
            response.set_cookie(utils.COOKIE_AUTHOR, author_name,
                                max_age=864000)
            response.set_cookie(utils.COOKIE_LANGUAGE, language)
            return response

    pastes = utils.get_pastes(context, request, 10)

    return dict(
        api = utils.API(context, request),
        author_name = author_name,
        paste = paste,
        lexers = utils.lexer_info,
        message = message,
        pastes = pastes,
        pastebin_url = pastebin_url,
        can_manage = can_manage,
        manage_url = resource_url(context, request, 'manage'),
        )
    
@view_config(for_=IPasteBin, name='manage', permission='manage',
             renderer='marlton.views:templates/pastebin_manage.pt')
def pastebin_manage_view(context, request):
    params = request.params
    message = params.get('message', u'')

    if params.has_key('form.submitted'):
        form = marshal(request.environ, request.body_file)
        checkboxes = form.get('delete', [])
        for checkbox in checkboxes:
            del context[checkbox]
        message = '%s pastes deleted' % len(checkboxes)
        url = resource_url(context, request, 'manage',
                           query={'message':message})
        response = HTTPFound(location=url)
        response.headers['Location'] = url
        return response

    pastebin_url = resource_url(context, request)
    pastes = utils.get_pastes(context, request, sys.maxint)

    return dict(
        api = utils.API(context, request),
        pastes = pastes,
        message = message,
        pastebin_url = pastebin_url,
        )
        
@view_config(for_=IPasteBin, name='rss', permission='view',
             renderer='marlton.views:templates/pastebin_rss.pt')
def pastebin_rss_view(context, request):
    pastebin_url = resource_url(context, request)
    pastes = utils.get_pastes(context, request, sys.maxint)
    if pastes:
        last_date=pastes[0]['date']
    else:
        last_date=None
    for paste in pastes:
        paste['body'] = utils.nl_to_br(paste['body'])
    response = dict(
        pastes = pastes,
        last_date = last_date,
        pastebin_url = pastebin_url,
        )
    request.response_content_type = 'application/rss+xml'
    return response

class PasteAddSchema(formencode.Schema):
    allow_extra_fields = True
    paste_ = formencode.validators.NotEmpty()


