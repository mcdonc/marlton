import datetime
import os
import sys
import urlparse
import lxml.html
from lxml import etree
from StringIO import StringIO

from zope.component import getUtility
from zope.index.text.parsetree import ParseError

from webob import Response
from webob.exc import HTTPFound

import formencode

from pygments import highlight
from pygments import util
from pygments import lexers

from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.interfaces import ISettings
from repoze.bfg.interfaces import ISecurityPolicy
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import has_permission
from repoze.bfg.security import Allow
from repoze.bfg.traversal import find_interface
from repoze.bfg.traversal import find_model
from repoze.bfg.view import bfg_view
from repoze.bfg.view import static
from repoze.bfg.url import model_url

from repoze.who.plugins.zodb.users import get_sha_password

from repoze.monty import marshal

from Captcha.Visual.Tests import PseudoGimpy

from bfgsite.models import Tutorial
from bfgsite.models import PasteEntry
from bfgsite.models import Profile

from bfgsite.interfaces import ITutorialBin
from bfgsite.interfaces import ITutorial
from bfgsite.interfaces import IPasteBin
from bfgsite.interfaces import IPasteEntry
from bfgsite.interfaces import IWebSite

from bfgsite.utils import preferred_author
from bfgsite.utils import COOKIE_AUTHOR
from bfgsite.utils import COOKIE_LANGUAGE
from bfgsite.utils import sort_byint
from bfgsite.utils import nl_to_br
from bfgsite.utils import API
from bfgsite.utils import lexer_info
from bfgsite.utils import formatter
from bfgsite.utils import style_defs
from bfgsite.utils import find_users
from bfgsite.utils import find_profiles

from bfgsite.catalog import find_catalog

static_dir = os.path.join(os.path.dirname(__file__), 'static')
static_app = static(static_dir)

@bfg_view(for_=IWebSite, name='static', permission='view')
def static_view(context, request):
    return static_app(context, request)

@bfg_view(for_=IWebSite, name='logout', permission='view')
def logout_view(context, request):
    policy = getUtility(ISecurityPolicy)
    headers = policy.auth.forget(request.environ, None)
    return HTTPFound(location=model_url(context, request), headers=headers)

@bfg_view(for_=IWebSite, name='login', permission='view')
def login_view(context, request):
    login = ''
    password = ''
    came_from = request.params.get('came_from')
    policy = getUtility(ISecurityPolicy)
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        users = find_users(context)
        info = users.get_by_login(login)
        if info:
            if info['password'] == get_sha_password(password):
                identity = {}
                identity['repoze.who.userid'] = info['id']
                headers = policy.auth.remember(request.environ, identity)
                if came_from:
                    return HTTPFound(location=came_from, headers=headers)
                else:
                    url = model_url(context, request, 'login')
                    return HTTPFound(location=url, headers=headers)

    logged_in = policy.authenticated_userid(request)
        
    return render_template_to_response(
        'templates/login.pt',
        api = API(context, request),
        login = login,
        password = password,
        logged_in = logged_in,
        came_from = came_from,
        )

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
        tutorial_url = model_url(tutorial, request)
        new = {
            'author':tutorial.author_name,
            'title':tutorial.title,
            'date':pdate,
            'url':tutorial_url,
            'language':tutorial.language,
            'name':name,
            'text':tutorial.text
            }
        tutorials.append(new)
    return tutorials

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
        )

class TutorialAddEditSchema(formencode.Schema):
    allow_extra_fields = True
    title = formencode.validators.NotEmpty()
    text = formencode.validators.NotEmpty()

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
        site = find_interface(context, IWebSite)
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
        url = url,
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
        site = find_interface(context, IWebSite)
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
            context.date = datetime.now()

    tutorials = get_tutorials(context, request, 10)

    return render_template_to_response(
        'templates/tutorialbin_addedit.pt',
        api = API(context, request),
        url = url,
        title = title,
        text = text,
        code = code,
        url = url,
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

class PasteAddSchema(formencode.Schema):
    allow_extra_fields = True
    paste = formencode.validators.NotEmpty()

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
        try:
            settings = getUtility(ISettings)
            from trac.env import open_environment
            trac_path = getattr(settings, 'trac.env_path')
            env = open_environment(trac_path, use_cache=False)
            search = TracSearch(env) 
            from trac.web.api import Request
            req = Request(request.environ, None)
            req.perm = All()
            trac_results = search.all_results(req, text)
            numdocs, docids = catalog.search(sort_index=sort_index,
                                             reverse=reverse,
                                             text=text)
            len_trac_results = len(trac_results)
            numdocs = numdocs + len_trac_results
            docids = list(docids)
            docids.extend([('trac', x) for x in range(len(trac_results))])
        except ParseError:
            numdocs, docids = 0, []
            trac_results = []
    else:
            numdocs, docids = 0, []
            trac_results = []

    i = 0

    batch = []

    trac_url = model_url(context, request, 'trac')

    if numdocs > 0:
        for docid in docids:
            i += 1
            if i > batch_start+ batch_size:
                break
            if i < batch_start:
                continue
            if isinstance(docid, tuple):
                md = {}
                trac_idx = docid[1]
                result = trac_results[trac_idx]
                md['url'] = trac_url + result[0]
                title = str(result[1])
                if title.endswith(' ...'):
                    title = title[:-4]
                md['title'] = title
                md['teaser'] = result[4]
                md['type'] = 'Trac'
            else:
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
                    md['url'] = rest
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

@bfg_view(name='trac', for_=IWebSite, permission='view')
def trac_view(context, request):
    theme = render_template('templates/trac_theme.pt',
                            api=API(context, request))
    settings = getUtility(ISettings)
    import trac.web.main
    trac_app = trac.web.main.dispatch_request
    from trac.web import HTTPException
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
        response.body = body
    return response

@bfg_view(for_=IWebSite, name='register', permission='view')
def register_view(context, request):
    logged_in = authenticated_userid(request)
    login = request.params.get('login', '')
    fullname = request.params.get('fullname', '')
    email = request.params.get('email', '')
    password = request.params.get('password', '')
    password_verify = request.params.get('password_verify')
    captcha_answer = request.params.get('captcha_answer', '')
    message = ''

    if 'form.submitted' in request.params:
        schema = RegisterSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            ok = False
            session = context.sessions.get(request.environ['repoze.browserid'])
            solutions = session.get('captcha_solutions', [])
            for solution in solutions:
                if captcha_answer.lower() == solution.lower():
                    ok = True
            if not ok:
                message = 'Bad CAPTCHA answer'
            else:
                users = find_users(context)
                info = users.get_by_login(login)
                if info:
                    message = 'Username %s already exists' % login
                else:
                    if password != password_verify:
                        message = 'Password and password verify do not match'
                    else:
                        users.add(login, login, password, groups=('members',))
                        profiles = find_profiles(context)
                        profile = Profile(fullname, email)
                        profiles[login] = profile
                        identity = {}
                        identity['repoze.who.userid'] = login
                        policy = getUtility(ISecurityPolicy)
                        headers = policy.auth.forget(request.environ, None)
                        headers = policy.auth.remember(request.environ,
                                                       identity)
                        login_url = model_url(context, request, 'login')
                        response = HTTPFound(location = login_url,
                                             headers=headers)
                        return response
        
    return render_template_to_response(
        'templates/register.pt',
        api = API(context, request),
        logged_in = logged_in,
        message = message,
        email = email,
        login = login,
        fullname = fullname,
        password = password,
        password_verify = password_verify,
        captcha_answer = captcha_answer,
        )

class RegisterSchema(formencode.Schema):
    allow_extra_fields = True
    login = formencode.validators.NotEmpty()
    fullname = formencode.validators.NotEmpty()
    email = formencode.validators.NotEmpty()
    password = formencode.validators.NotEmpty()
    password_verify = formencode.validators.NotEmpty()
    captcha_answer = formencode.validators.NotEmpty()

class All(object):
    def __call__(self, other):
        return self

    def __contains__(self, other):
        return True

from trac.search.web_ui import SearchModule

class TracSearch(SearchModule):
    def all_results(self, req, term):
        query = self._get_search_terms(term)
        results = []
        for source in self.search_sources:
            for result in source.get_search_results(req, query,
                                                    ['ticket', 'wiki']):
                results.append(result)
        return results

utf8_html_parser = lxml.html.HTMLParser(encoding='utf-8')
