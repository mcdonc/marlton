import datetime
import sys

from webob.exc import HTTPFound
from webob import Response

import formencode

from pygments import lexers
from pygments import util
from pygments import highlight


from pyramid.security import Allow
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.url import resource_url
from pyramid.view import view_config

from repoze.monty import marshal

from marlton.interfaces import ITutorialBin
from marlton.interfaces import ITutorial

from marlton.models import Tutorial

from marlton.utils import API
from marlton.utils import COOKIE_LANGUAGE
from marlton.utils import formatter
from marlton.utils import get_tutorials
from marlton.utils import style_defs
from marlton.utils import nl_to_br
from marlton.utils import lexer_info

@view_config(for_=ITutorial, permission='view',
             renderer='marlton.views:templates/tutorial.pt')
def tutorial_view(context, request):
    text = context.text or u''
    try:
        if context.language:
            l = lexers.get_lexer_by_name(context.language)
        else:
            l = lexers.guess_lexer(context.code)
    except util.ClassNotFound:
        # couldn't guess lexer
        l = lexers.TextLexer()

    formatted_tutorial = highlight(context.code, l, formatter)
    tutorials = get_tutorials(context, request, 10)
    can_edit = has_permission('edit', context, request)
    
    attachment_url = None
    if context.attachment_name is not None:
        attachment_url = request.url + '/download_attachment'

    return dict(
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
        edit_url = resource_url(context, request, 'edit'),
        delete_url = resource_url(context, request, 'delete'),
        tutorialbin_url = resource_url(context.__parent__, request),
        attachment_url = attachment_url,
        attachment_mimetype = context.attachment_mimetype,
        attachment_name = context.attachment_name,
        )
        
@view_config(for_=ITutorial, name='download_attachment', permission='view')
def download_attachement(context, request):
    f = context.attachment_data.open()
    headers = [
        ('Content-Disposition', 
            'attachment;filename='+context.attachment_name),
        ('Content-Type', context.attachment_mimetype),
        ]
    response = Response(headerlist=headers, app_iter=f)
    return response                

@view_config(for_=ITutorialBin, permission='view',
             renderer='marlton.views:templates/tutorialbin.pt')
def tutorialbin_view(context,request):
    tutorialbin_url = resource_url(context, request)
    tutorials = get_tutorials(context, request, sys.maxint)
    if tutorials:
        last_date = tutorials[0]['date']
        latest_obj = context[tutorials[0]['name']]
        try:
            if latest_obj.language:
                l = lexers.get_lexer_by_name(latest_obj.language)
            else:
                l = lexers.guess_lexer(latest_obj.code)
        except util.ClassNotFound:
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
    return dict(
        api = API(context, request),
        tutorials = tutorials,
        style_defs = style_defs,
        last_date = last_date,
        latest = latest,
        message = None,
        tutorialbin_url = tutorialbin_url,
        user = user,
        can_manage = can_manage,
        manage_url = resource_url(context, request, 'manage'),
        )

@view_config(for_=ITutorialBin, name='add', permission='add',
             renderer='marlton.views:templates/tutorialbin_addedit.pt')
def tutorialbin_add_view(context, request):
    params = request.params
    title = u''
    url = u''
    language = u''
    text = u''
    code = u''
    message = u''
    attachment= ''
    tutorialbin_url = resource_url(context, request)
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)

    if params.has_key('form.submitted'):
        title = params.get('title', u'')
        text = params.get('text', u'')
        code = params.get('code', u'')
        url = params.get('url', u'')
        language = params.get('language', u'')
        schema = TutorialAddEditSchema()
        message = None
        attachment = params.get('attachment')
        try:
            schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            file_name = None
            mime_type = None
            stream = None
            if hasattr(attachment, 'filename'):
                file_name = attachment.filename
                mime_type = attachment.type
                stream = attachment.file
            pobj = Tutorial(title, user, text, url, code, language, 
                            stream, file_name, mime_type)
            acl = context.__acl__[:]
            acl.extend([(Allow, user, 'edit'), (Allow, 'admin', 'edit')])
            pobj.__acl__ = acl
            tutorialid = context.add_item(pobj)
            response = HTTPFound(location = '%s%s' % (tutorialbin_url,
                                                      tutorialid))
            response.set_cookie(COOKIE_LANGUAGE, language)
            return response

    tutorials = get_tutorials(context, request, 10)

    return dict(
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
        form_url = resource_url(context, request, 'add'),
        )

@view_config(for_=ITutorial, name='edit', permission='edit',
             renderer='marlton.views:templates/tutorialbin_addedit.pt')
def tutorial_edit_view(context, request):
    message = u''
    title = context.title
    url = context.url
    language = context.language
    text = context.text
    code = context.code
    tutorialbin_url = resource_url(context.__parent__, request)
    user = authenticated_userid(request)
    can_manage = has_permission('manage', context, request)

    params = request.params
    if params.has_key('form.submitted'):
        title = params.get('title', u'')
        url = params.get('url', u'')
        language = params.get('language', u'')
        text = params.get('text', u'')
        code = params.get('code', u'')
        schema = TutorialAddEditSchema()
        message = None
        attachment = params.get('attachment', u'')
        try:
            schema.to_python(request.params)
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
            if attachment != u'':
                context.attachment_name = attachment.filename
                context.attachment_mimetype = attachment.type
                context.upload(attachment.file)

    tutorials = get_tutorials(context, request, 10)

    return dict(
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
        form_url = resource_url(context, request, 'edit'),
        )

@view_config(for_=ITutorial, name='delete', permission='edit',
             renderer='marlton.views:templates/areyousure.pt')
def delete_tutorial_view(context, request):
    parent = context.__parent__
    if 'form.yes' in request.params:
        name = context.__name__
        del parent[name]
        return HTTPFound(location=resource_url(parent, request))
    if 'form.no' in request.params:
        return HTTPFound(location=resource_url(context, request))
    return dict(
        api = API(context, request),
        form_url = resource_url(context, request, 'delete'),
        message = 'Are you sure you want to delete "%s"' % context.title
        )
    
@view_config(for_=ITutorialBin, name='manage', permission='manage',
             renderer='marlton.views:templates/tutorialbin_manage.pt')
def tutorialbin_manage_view(context, request):
    params = request.params
    message = params.get('message', u'')

    if params.has_key('form.submitted'):
        form = marshal(request.environ, request.body_file)
        checkboxes = form.get('delete', [])
        for checkbox in checkboxes:
            del context[checkbox]
        message = '%s tutorials deleted' % len(checkboxes)
        url = resource_url(context, request, 'manage',
                           query={'message':message})
        response = HTTPFound(location=url)
        return response

    tutorials = get_tutorials(context, request, sys.maxint)
    tutorialbin_url = resource_url(context, request)

    return dict(
        api = API(context, request),
        message = message,
        tutorials = tutorials,
        tutorialbin_url = tutorialbin_url,
        )
        
@view_config(for_=ITutorialBin, name='rss', permission='view',
             renderer='marlton.views:templates/tutorialbin_rss.pt')
def tutorialbin_rss_view(context, request):
    tutorialbin_url = resource_url(context, request)
    tutorials = get_tutorials(context, request, sys.maxint)
    if tutorials:
        last_date=tutorials[0]['date']
    else:
        last_date=None
    for tutorial in tutorials:
        tutorial['text'] = nl_to_br(tutorial['text'])
    response = dict(
        tutorials = tutorials,
        last_date = last_date,
        tutorialbin_url = tutorialbin_url,
        )
    request.response_content_type = 'application/rss+xml'
    return response

class TutorialAddEditSchema(formencode.Schema):
    allow_extra_fields = True
    title = formencode.validators.NotEmpty()
    text = formencode.validators.NotEmpty()

