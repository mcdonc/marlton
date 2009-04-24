import datetime
import sys

from webob.exc import HTTPFound

import formencode

from pygments import lexers
from pygments import util
from pygments import highlight


from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.security import Allow
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.bfg.view import bfg_view

from repoze.monty import marshal

from bfgsite.interfaces import ITutorialBin
from bfgsite.interfaces import ITutorial

from bfgsite.models import Tutorial

from bfgsite.utils import API
from bfgsite.utils import COOKIE_LANGUAGE
from bfgsite.utils import find_site
from bfgsite.utils import formatter
from bfgsite.utils import get_tutorials
from bfgsite.utils import style_defs
from bfgsite.utils import nl_to_br
from bfgsite.utils import lexer_info

@bfg_view(for_=ITutorial, permission='view')
def tutorial_view(context, request):
    text = context.text or u''
    try:
        if context.language:
            l = lexers.get_lexer_by_name(context.language)
        else:
            l = lexers.guess_lexer(context.code)
        language = l.aliases[0]
    except util.ClassNotFound, err:
        # couldn't guess lexer
        l = lexers.TextLexer()

    formatted_tutorial = highlight(context.code, l, formatter)
    tutorials = get_tutorials(context, request, 10)
    can_edit = has_permission('edit', context, request)

    return render_template_to_response(
        'templates/tutorial.pt',
        api = API(context, request),
        author = context.author_name,
        url = context.url,
        date = context.date.strftime('%x at %X'),
        style_defs = style_defs,
        lexer_name = l.name,
        code = formatted_tutorial,
        text = text,
        tutorials = tutorials,
        message = None,
        title = context.title,
        can_edit = can_edit,
        edit_url = model_url(context, request, 'edit'),
        delete_url = model_url(context, request, 'delete'),
        tutorialbin_url = model_url(context.__parent__, request)
        )

@bfg_view(for_=ITutorialBin, permission='view')
def tutorialbin_view(context,request):
    tutorialbin_url = model_url(context, request)
    tutorials = get_tutorials(context, request, sys.maxint)
    if tutorials:
        last_date = tutorials[0]['date']
        latest_obj = context[tutorials[0]['name']]
        try:
            if latest_obj.language:
                l = lexers.get_lexer_by_name(latest_obj.language)
            else:
                l = lexers.guess_lexer(latest_obj.code)
            language = l.aliases[0]
        except util.ClassNotFound, err:
            l = lexers.TextLexer()
        formatted_code= highlight(latest_obj.code, l, formatter)
        latest = {'author_name':latest_obj.author_name,
                  'date':latest_obj.date,
                  'title':latest_obj.title,
                  'text':latest_obj.text,
                  'formatted_code':formatted_code,
                  'url':latest_obj.url}
    else:
        last_date = None
        latest = None
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)
    return render_template_to_response(
        'templates/tutorialbin.pt',
        api = API(context, request),
        tutorials = tutorials,
        style_defs = style_defs,
        last_date = last_date,
        latest = latest,
        message = None,
        tutorialbin_url = tutorialbin_url,
        user = user,
        can_manage = can_manage,
        manage_url = model_url(context, request, 'manage'),
        )

@bfg_view(for_=ITutorialBin, name='add', permission='add')
def tutorialbin_add_view(context, request):
    params = request.params
    title = u'',
    url = u''
    language = u''
    text = u''
    code = u''
    message = u''
    tutorialbin_url = model_url(context, request)
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)

    if params.has_key('form.submitted'):
        site = find_site(context)
        title = params.get('title', u'')
        text = params.get('text', u'')
        code = params.get('code', u'')
        url = params.get('url', u'')
        language = params.get('language', u'')
        schema = TutorialAddEditSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:

            pobj = Tutorial(title, user, text, url, code, language)
            acl = context.__acl__[:]
            acl.extend([(Allow, user, 'edit'), (Allow, 'admin', 'edit')])
            pobj.__acl__ = acl
            tutorialid = context.add(pobj)
            response = HTTPFound(location = '%s%s' % (tutorialbin_url,
                                                      tutorialid))
            response.set_cookie(COOKIE_LANGUAGE, language)
            return response

    tutorials = get_tutorials(context, request, 10)

    return render_template_to_response(
        'templates/tutorialbin_addedit.pt',
        api = API(context, request),
        url = url,
        title = title,
        text = text,
        code = code,
        lexers = lexer_info,
        message = message,
        tutorials = tutorials,
        tutorialbin_url = tutorialbin_url,
        user = user,
        can_manage = can_manage,
        pagetitle = 'Add a Tutorial',
        form_url = model_url(context, request, 'add'),
        )

@bfg_view(for_=ITutorial, name='edit', permission='edit')
def tutorial_edit_view(context, request):
    message = u''
    title = context.title
    url = context.url
    language = context.language
    text = context.text
    code = context.code
    tutorialbin_url = model_url(context.__parent__, request)
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)

    params = request.params
    if params.has_key('form.submitted'):
        site = find_site(context)
        title = params.get('title', u'')
        url = params.get('url', u'')
        language = params.get('language', u'')
        text = params.get('text', u'')
        code = params.get('code', u'')
        schema = TutorialAddEditSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            message = 'Tutorial edited'
            context.title = title
            context.text = text
            context.url = url
            context.code = code
            context.language = language
            context.date = datetime.datetime.now()

    tutorials = get_tutorials(context, request, 10)

    return render_template_to_response(
        'templates/tutorialbin_addedit.pt',
        api = API(context, request),
        url = url,
        title = title,
        text = text,
        code = code,
        lexers = lexer_info,
        message = message,
        tutorials = tutorials,
        tutorialbin_url = tutorialbin_url,
        user = user,
        can_manage = can_manage,
        pagetitle = 'Edit a Tutorial',
        form_url = model_url(context, request, 'edit'),
        )

@bfg_view(for_=ITutorial, name='delete', permission='edit')
def delete_tutorial_view(context, request):
    parent = context.__parent__
    if 'form.yes' in request.params:
        name = context.__name__
        del parent[name]
        return HTTPFound(location=model_url(parent, request))
    if 'form.no' in request.params:
        return HTTPFound(location=model_url(context, request))
    return render_template_to_response(
        'templates/areyousure.pt',
        api = API(context, request),
        form_url = model_url(context, request, 'delete'),
        message = 'Are you sure you want to delete "%s"' % context.title
        )
    
@bfg_view(for_=ITutorialBin, name='manage', permission='manage')
def tutorialbin_manage_view(context, request):
    params = request.params
    message = params.get('message', u'')

    if params.has_key('form.submitted'):
        form = marshal(request.environ, request.body_file)
        checkboxes = form.get('delete', [])
        for checkbox in checkboxes:
            del context[checkbox]
        message = '%s tutorials deleted' % len(checkboxes)
        url = model_url(context, request, 'manage', query={'message':message})
        response = HTTPFound(location=url)
        return response

    tutorials = get_tutorials(context, request, sys.maxint)
    tutorialbin_url = model_url(context, request)

    return render_template_to_response(
        'templates/tutorialbin_manage.pt',
        api = API(context, request),
        message = message,
        tutorials = tutorials,
        tutorialbin_url = tutorialbin_url,
        )
        
@bfg_view(for_=ITutorialBin, name='rss', permission='view')
def tutorialbin_rss_view(context, request):
    tutorialbin_url = model_url(context, request)
    tutorials = get_tutorials(context, request, sys.maxint)
    if tutorials:
        last_date=tutorials[0]['date']
    else:
        last_date=None
    for tutorial in tutorials:
        tutorial['text'] = nl_to_br(tutorial['text'])
    response = render_template_to_response(
        'templates/tutorialbin_rss.pt',
        tutorials = tutorials,
        last_date = last_date,
        tutorialbin_url = tutorialbin_url,
        )
    response.content_type = 'application/rss+xml'
    return response

class TutorialAddEditSchema(formencode.Schema):
    allow_extra_fields = True
    title = formencode.validators.NotEmpty()
    text = formencode.validators.NotEmpty()

