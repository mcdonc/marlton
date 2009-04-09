import sys
import urlparse

import formencode
import webob

import pygments
from pygments import lexers
from pygments import formatters
from pygments import util

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.traversal import find_interface
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.url import model_url
from repoze.monty import marshal

from bfgsite.models import Tutorial
from bfgsite.models import ITutorialBin

from bfgsite.utils import preferred_author
from bfgsite.utils import COOKIE_AUTHOR
from bfgsite.utils import COOKIE_LANGUAGE
from bfgsite.utils import sort_byint

def get_tutorials(context, request, max):
    tutorialbin = find_interface(context, ITutorialBin)
    tutorials = []
    tutorialbin_url = model_url(tutorialbin, request)
    keys = sort_byint(tutorialbin.keys())
    keys = keys[:max]
    for name in keys:
        tutorial = tutorialbin[name]
        if tutorial.date is not None:
            pdate = tutorial.date.strftime('%x')
        else:
            pdate = 'UNKNOWN'
        tutorial_url = urlparse.urljoin(tutorialbin_url, name)
        new = {'author':tutorial.author_name, 'title':tutorial.title, 'date':pdate, 'url':tutorial_url, 'author_url':tutorial.author_url, 'language':tutorial.language,'name':name}
        tutorials.append(new)
    return tutorials

formatter = formatters.HtmlFormatter(linenos=True,
                                     cssclass="source")
style_defs = formatter.get_style_defs()

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

    formatted_tutorial = pygments.highlight(context.code, l, formatter)
    tutorials = get_tutorials(context, request, 10)

    return render_template_to_response(
        'templates/tutorial.pt',
        author = context.author_name,
        author_url = context.author_url,
        date = context.date.strftime('%x at %X'),
        style_defs = style_defs,
        lexer_name = l.name,
        code = formatted_tutorial,
        text = text,
        tutorials = tutorials,
        message = None,
        application_url = request.application_url,
        title = context.title,
        tutorialbin_url = model_url(context.__parent__, request)
        )

all_lexers = list(lexers.get_all_lexers())
all_lexers.sort()
lexer_info = []
for name, aliases, filetypes, mimetypes_ in all_lexers:
    lexer_info.append({'alias':aliases[0], 'name':name})

def tutorialbin_view(context,request):
    response = webob.Response()
    app_url = request.application_url
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
        formatted_code= pygments.highlight(latest_obj.code, l, formatter)
        latest = {'author_name':latest_obj.author_name, 'date':latest_obj.date, 'title':latest_obj.title, 'text':latest_obj.text, 'formatted_code':formatted_code, 'author_url':latest_obj.author_url}
    else:
        last_date = None
        latest = None
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)
    body = render_template(
        'templates/tutorialbin.pt',
        tutorials = tutorials,
        style_defs = style_defs,
        last_date = last_date,
        latest = latest,
        message = None,
        application_url = app_url,
        tutorialbin_url = tutorialbin_url,
        user = user,
        can_manage = can_manage,
        )
    response.unicode_body = unicode(body)
    return response    

class TutorialAddSchema(formencode.Schema):
    allow_extra_fields = True
    author_name = formencode.validators.NotEmpty()
    title = formencode.validators.NotEmpty()
    text = formencode.validators.NotEmpty()

def tutorialbin_add_view(context, request):
    params = request.params
    author_name = preferred_author(request)
    title = u'',
    author_url = u''
    language = u''
    text = u''
    code = u''
    message = u''
    response = webob.Response()
    app_url = request.application_url
    tutorialbin_url = model_url(context, request)
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)

    if params.has_key('form.submitted'):
        title = request.params.get('title', '')
        text = request.params.get('text', '')
        code = request.params.get('code', '')
        author_name = request.params.get('author_name', '')
        author_url = request.params.get('author_url', '')
        language = request.params.get('language', '')
        schema = TutorialAddSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            response.set_cookie(COOKIE_AUTHOR, author_name)
            response.set_cookie(COOKIE_LANGUAGE, language)

            if isinstance(title, str):
                title = unicode(title, 'utf-8')
            if isinstance(author_name, str):
                author_name = unicode(author_name, 'utf-8')
            if isinstance(author_url, str):
                author_url = unicode(author_url, 'utf-8')
            if isinstance(language, str):
                language = unicode(language, 'utf-8')
            if isinstance(text, str):
                text = unicode(text, 'utf-8')
            if isinstance(code, str):
                code = unicode(code, 'utf-8')

            pobj = Tutorial(title, author_name, text, author_url, code, language)
            tutorialid = context.add(pobj)
            response.status = '301 Moved Permanently'
            response.headers['Location'] = '%s%s' % (tutorialbin_url, tutorialid)
    tutorials = get_tutorials(context, request, 10)

    body = render_template(
        'templates/tutorialbin_add.pt',
        author_name = author_name,
        author_url = author_url,
        title = title,
        text = text,
        code = code,
        lexers = lexer_info,
        message = message,
        tutorials = tutorials,
        application_url = app_url,
        tutorialbin_url = tutorialbin_url,
        user = user,
        can_manage = can_manage,
        )
    response.unicode_body = unicode(body)
    return response

def tutorialbin_manage_view(context, request):
    params = request.params
    message = u''
    response = webob.Response()
    app_url = request.application_url
    tutorialbin_url = model_url(context, request)

    if params.has_key('form.submitted'):
        form = marshal(request.environ, request.body_file)
        checkboxes = form.get('delete', [])
        for checkbox in checkboxes:
            del context[checkbox]
        message = '%s tutorials deleted' % len(checkboxes)
        response.status = '301 Moved Permanently'
        response.headers['Location'] = tutorialbin_url

    tutorials = get_tutorials(context, request, sys.maxint)

    body = render_template(
        'templates/tutorialbin_manage.pt',
        tutorials = tutorials,
        application_url = app_url,
        tutorialbin_url = tutorialbin_url,
        )
    response.unicode_body = unicode(body)
    return response
        
def tutorialbin_rss_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    tutorialbin_url = model_url(context, request)
    tutorials = get_tutorials(context, request, sys.maxint)
    if tutorials:
        last_date=tutorials[0]['date']
    else:
        last_date=None
    body = render_template(
        'templates/tutorialbin_rss.pt',
        tutorials = tutorials,
        last_date = last_date,
        application_url = app_url,
        tutorialbin_url = tutorialbin_url,
        )
    response.unicode_body = unicode(body)
    return response    
