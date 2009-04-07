import os
import sys
import urlparse

import formencode
import webob

from paste import urlparser

from repoze.bfg.wsgi import wsgiapp
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.url import model_url

from bfgsite.utils import sort_byint

COOKIE_LANGUAGE = 'website.last_lang'
COOKIE_AUTHOR = 'website.last_author'

here = os.path.abspath(os.path.dirname(__file__))
static = urlparser.StaticURLParser(os.path.join(here, 'static', '..'))

@wsgiapp
def static_view(environ, start_response):
    return static(environ, start_response)

def preferred_author(request):
    author_name = request.params.get('author_name', u'')
    if not author_name:
        author_name = request.cookies.get(COOKIE_AUTHOR, u'')
    if isinstance(author_name, str):
        author_name = unicode(author_name, 'utf-8')
    return author_name

def manage_view(context, request):
    params = request.params
    message = u''
    response = webob.Response()
    app_url = request.application_url
    pastebin_url = model_url(context['pastebin'], request)
    tutorialbin_url = model_url(context['tutorialbin'], request)

    body = render_template(
        'templates/manage.pt',
        application_url = app_url,
        pastebin_url = pastebin_url,
        tutorialbin_url = tutorialbin_url,
        )
    response.unicode_body = unicode(body)
    return response
        
def logout_view(context, request):
    response = webob.Response()
    response.status = '401 Unauthorized'
    return response

def index_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    body = render_template(
        'templates/index.pt',
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response    

def docs_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    body = render_template(
        'templates/documentation.pt',
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response    
def install_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    body = render_template(
        'templates/install.pt',
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response    

def community_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    body = render_template(
        'templates/community.pt',
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response    

def software_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    body = render_template(
        'templates/software.pt',
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response    
