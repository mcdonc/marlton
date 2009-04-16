import os
import sys
import urlparse
from StringIO import StringIO

from zope.component import getUtility

from webob import Response
from webob.exc import HTTPUnauthorized

import formencode

from pygments import lexers
from pygments import formatters
from pygments import highlight
from pygments import util

from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.interfaces import ISettings
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.traversal import find_interface
from repoze.bfg.traversal import find_model
from repoze.bfg.view import bfg_view
from repoze.bfg.view import static
from repoze.bfg.url import model_url
from repoze.bfg.wsgi import wsgiapp

from repoze.monty import marshal

from Captcha.Visual.Tests import PseudoGimpy

from bfgsite.models import Tutorial
from bfgsite.models import PasteEntry

from bfgsite.interfaces import ITutorialBin
from bfgsite.interfaces import IPasteBin
from bfgsite.interfaces import IPasteEntry
from bfgsite.interfaces import IWebSite
from bfgsite.interfaces import ITutorial

from bfgsite.utils import preferred_author
from bfgsite.utils import COOKIE_AUTHOR
from bfgsite.utils import COOKIE_LANGUAGE
from bfgsite.utils import sort_byint
from bfgsite.utils import nl_to_br

from bfgsite.catalog import find_catalog

static_dir = os.path.join(os.path.dirname(__file__), 'static')
static_app = static(static_dir)

@bfg_view(for_=IWebSite, name='static', permission='view')
def static_view(context, request):
    return static_app(context, request)

@bfg_view(for_=IWebSite, name='logout', permission='view')
def logout_view(context, request):
    return HTTPUnauthorized()

@bfg_view(for_=IWebSite, permission='view')
def index_view(context, request):
    tutorials = get_tutorials(context['tutorialbin'], request, 5)
    return render_template_to_response(
        'templates/index.pt',
        api = API(context, request),
        tutorials = tutorials,
        )

@bfg_view(for_=IWebSite, name='documentation', permission='view')
def docs_view(context, request):
    return render_template_to_response(
        'templates/documentation.pt',
        api = API(context, request),
        )

@bfg_view(for_=IWebSite, name='community', permission='view')
def community_view(context, request):
    return render_template_to_response(
        'templates/community.pt',
        api = API(context, request),
        )

@bfg_view(for_=IWebSite, name='software', permission='view')
def software_view(context, request):
    return render_template_to_response(
        'templates/software.pt',
        api = API(context, request),
        )

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
        new = {
            'author':tutorial.author_name,
            'title':tutorial.title,
            'date':pdate,
            'url':tutorial_url,
            'author_url':tutorial.author_url,
            'language':tutorial.language,
            'name':name,
            'text':tutorial.text
            }
        tutorials.append(new)
    return tutorials

formatter = formatters.HtmlFormatter(linenos=True,
                                     cssclass="source")
style_defs = formatter.get_style_defs()

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

    return render_template_to_response(
        'templates/tutorial.pt',
        api = API(context, request),
        author = context.author_name,
        author_url = context.author_url,
        date = context.date.strftime('%x at %X'),
        style_defs = style_defs,
        lexer_name = l.name,
        code = formatted_tutorial,
        text = text,
        tutorials = tutorials,
        message = None,
        title = context.title,
        tutorialbin_url = model_url(context.__parent__, request)
        )

all_lexers = list(lexers.get_all_lexers())
all_lexers.sort()
lexer_info = []
for name, aliases, filetypes, mimetypes_ in all_lexers:
    lexer_info.append({'alias':aliases[0], 'name':name})

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
                  'author_url':latest_obj.author_url}
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
        )

class TutorialAddSchema(formencode.Schema):
    allow_extra_fields = True
    author_name = formencode.validators.NotEmpty()
    title = formencode.validators.NotEmpty()
    text = formencode.validators.NotEmpty()

@bfg_view(for_=ITutorialBin, name='add', permission='view')
def tutorialbin_add_view(context, request):
    params = request.params
    author_name = preferred_author(request)
    title = u'',
    author_url = u''
    language = u''
    text = u''
    code = u''
    message = u''
    tutorialbin_url = model_url(context, request)
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)

    if params.has_key('form.submitted'):
        site = find_interface(context, IWebSite)
        session = site.sessions.get(request.environ['repoze.browserid'])
        solutions = session.get('captcha_solutions', [])
        captcha_answer = params.get('captcha_answer', '')
        ok = False
        for solution in solutions:
            if captcha_answer.lower() == solution.lower():
                ok = True
        if not ok:
            message = 'Bad CAPTCHA answer'
        else:
            title = params.get('title', u'')
            text = params.get('text', u'')
            code = params.get('code', u'')
            author_name = params.get('author_name', u'')
            author_url = params.get('author_url', u'')
            language = params.get('language', u'')
            schema = TutorialAddSchema()
            message = None
            try:
                form = schema.to_python(request.params)
            except formencode.validators.Invalid, why:
                message = str(why)
            else:
                response = Response()
                response.set_cookie(COOKIE_AUTHOR, author_name, max_age=864000)
                response.set_cookie(COOKIE_LANGUAGE, language)

                pobj = Tutorial(title, author_name, text, author_url, code,
                                language)
                tutorialid = context.add(pobj)
                response.status = '302'
                response.headers['Location'] = '%s%s' % (tutorialbin_url,
                                                         tutorialid)
                return response

    tutorials = get_tutorials(context, request, 10)

    return render_template_to_response(
        'templates/tutorialbin_add.pt',
        api = API(context, request),
        author_name = author_name,
        author_url = author_url,
        title = title,
        text = text,
        code = code,
        lexers = lexer_info,
        message = message,
        tutorials = tutorials,
        tutorialbin_url = tutorialbin_url,
        user = user,
        can_manage = can_manage,
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
        response = Response()
        response.status = '302'
        url = model_url(context, request, 'manage', query={'message':message})
        response.headers['Location'] = url
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
        author_name = entry.author_name
        if not author_name:
            author_name = '{unknown}'
        paste_title = '#%s by %s on %s (%s...)' % (name, author_name[:15],
                                                   pdate, entry.paste[:8])
        new = {'author':author_name, 'date':pdate, 'url':paste_url,
               'language':entry.language,'name':name, 'body':entry.paste,
               'title':paste_title}
        pastes.append(new)
    return pastes

formatter = formatters.HtmlFormatter(linenos=True,
                                     cssclass="source")
style_defs = formatter.get_style_defs()

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
        'templates/entry.pt',
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

all_lexers = list(lexers.get_all_lexers())
all_lexers.sort()
lexer_info = []
for name, aliases, filetypes, mimetypes_ in all_lexers:
    lexer_info.append({'alias':aliases[0], 'name':name})

class PasteAddSchema(formencode.Schema):
    allow_extra_fields = True
    paste = formencode.validators.NotEmpty()

@bfg_view(for_=IPasteBin, permission='view')
def pastebin_view(context, request):
    params = request.params
    author_name = preferred_author(request)
    language = u''
    paste = u''
    message = u''
    pastebin_url = model_url(context, request)
    user = authenticated_userid(request)
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
            response = Response()
            response.set_cookie(COOKIE_AUTHOR, author_name, max_age=864000)
            response.set_cookie(COOKIE_LANGUAGE, language)
            pobj = PasteEntry(author_name, paste, language)
            pasteid = context.add(pobj)
            response.status = '302'
            response.headers['Location'] = '%s%s' % (pastebin_url, pasteid)
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
        user = user,
        can_manage = can_manage,
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
        response = Response()
        response.status = '302'
        url = model_url(context, request, 'manage', query={'message':message})
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

@bfg_view(name='captcha.jpg')
def captcha_jpeg(context, request):
    site = find_interface(context, IWebSite)
    output = StringIO()
    
    captcha = PseudoGimpy()
    image = captcha.render()
    image.save(output, 'JPEG')
    data = output.getvalue()
    session = site.sessions.get(request.environ['repoze.browserid'])
    session['captcha_solutions'] = captcha.solutions
    r = Response(data, '200 OK', [ ('Content-Type', 'image/jpeg'),
                                   ('Content-Length', len(data)) ])
    return r

@bfg_view(name='searchresults', for_=IWebSite, permission='view')
def searchresults(context, request):
    posts = []
    catalog = find_catalog(context)

    text = request.params.get('text')
    batch_size = int(request.params.get('batch_size', 20))
    batch_start = int(request.params.get('batch_start', 0))
    sort_index = request.params.get('sort_index', None)
    reverse = bool(request.params.get('reverse', False))


    if text is not None:
        numdocs, docids = catalog.search(sort_index=sort_index,
                                         reverse=reverse,
                                         text=text)
    else:
        numdocs, docids = 0, []

    i = 0

    batch = []

    if numdocs > 0:
        for docid in docids:
            i += 1
            if i > batch_start+ batch_size:
                break
            if i < batch_start:
                continue
            path = catalog.document_map.address_for_docid(docid)
            md = dict(catalog.document_map.get_metadata(docid))
            if path.startswith('sphinx:'):
                scheme, rest = path.split(':', 1)
                if text.lower() in md['text'].lower():
                    firstpos = md['text'].lower().find(text.lower())
                else:
                    firstpos = 0
                start = firstpos -150
                if start < 0:
                    start = 0
                teaser = '%s ...' % md['text'][start:start+300]
                url = rest
                md['teaser'] = teaser
            else:
                model = find_model(context, path)
                url = model_url(model, request)
            md['url'] = url
            batch.append(md)

    def _batchURL(query, batch_start=0):
        query['batch_start'] = batch_start
        return model_url(context, request, request.view_name,
                         query=query)

    batch_info = {}

    previous_start = batch_start - batch_size

    if previous_start < 0:
        previous_batch_info = None
    else:
        previous_end = previous_start + batch_size
        if previous_end > numdocs:
            previous_end = numdocs
        size = previous_end - previous_start
        previous_batch_info = {}
        query = {'text':text, 'reverse':reverse, 'batch_size':batch_size}
        previous_batch_info['url'] = _batchURL(query, previous_start)
        previous_batch_info['name'] = (
            'Previous %s entries (%s - %s)' % (size, previous_start+1,
                                               previous_end))
    batch_info['previous_batch'] = previous_batch_info

    next_start = batch_start + batch_size
    if next_start >= numdocs:
        next_batch_info = None
    else:
        next_end = next_start + batch_size
        if next_end > numdocs:
            next_end = numdocs
        size = next_end - next_start
        next_batch_info = {}
        query = {'text':text, 'reverse':reverse, 'batch_size':batch_size}
        next_batch_info['url'] = _batchURL(query, next_start)
        next_batch_info['name'] = (
            'Next %s entries (%s - %s of %s)' % (size,
                                                 next_start+1,
                                                 next_end,
                                                 numdocs))
    batch_info['next_batch'] = next_batch_info
    batch_info['batching_required'] = next_batch_info or previous_batch_info

    return render_template_to_response(
        'templates/searchresults.pt',
        batch = batch,
        batch_info = batch_info,
        numdocs = numdocs,
        api = API(context, request),
        )



class API:
    nav_links = (
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite,),
         'view_name':'documentation',
         'title':'Documentation'},
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite,),
         'view_name':'software',
         'title':'Software'},
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite,),
         'view_name':'community',
         'title':'Community'},
        {'view_iface':IWebSite,
         'nav_ifaces':(IPasteBin, IPasteEntry),
         'view_name':'pastebin',
         'title':'Pastes'},
        {'view_iface':IWebSite,
         'nav_ifaces':(ITutorialBin, ITutorial),
         'view_name':'tutorialbin',
         'title':'Tutorials'},
        )
    def __init__(self, context, request):
        self.context = context
        self.site = find_interface(context, IWebSite)
        self.request = request
        self.main_template = get_template('templates/main_template.pt')
        self.navitems = get_navigation(context, request, self.nav_links)
        self.application_url = request.application_url

def get_navigation(context, request, links):

    items = []

    for link in links:
        state = 'notcurrent'
        view_iface = link['view_iface']
        nav_ifaces = link['nav_ifaces']
        view_name = link['view_name']

        if view_iface.providedBy(context):
            if request.view_name == view_name:
                state = 'current'
        else:
            for nav_iface in nav_ifaces:
                if nav_iface.providedBy(context):
                    state = 'current'
                    break

        viewcontext = find_interface(context, view_iface)

        if viewcontext is not None:

            items.append(
                {'state':state,
                 'href':model_url(viewcontext, request, view_name),
                 'title':link['title'],
                 })

    return items

@bfg_view(name='trac', for_=IWebSite, permission='view')
@wsgiapp
def trac_view(environ, start_response):
    settings = getUtility(ISettings)
    os.environ['TRAC_ENV_PARENT_DIR'] = settings.trac_env_parent_dir
    import trac.web.main
    trac_app = trac.web.main.dispatch_request
    from trac.web import HTTPException
    try:
        return trac_app(environ, start_response)
    except HTTPException, exc:
        r = Response()
        r.status_int = exc.code
        r.write(exc.message)
        return r(environ, start_response)
        
    
