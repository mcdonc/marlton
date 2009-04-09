import os
import webob

from paste import urlparser

from repoze.bfg.wsgi import wsgiapp
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import get_template

here = os.path.abspath(os.path.dirname(__file__))
static = urlparser.StaticURLParser(os.path.join(here))

@wsgiapp
def static_view(environ, start_response):
    return static(environ, start_response)

def logout_view(context, request):
    response = webob.Response()
    response.status = '401 Unauthorized'
    return response

def index_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    body = render_template(
        'templates/index.pt',
        main_template = get_template('templates/main_template.pt'),
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response    

def docs_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    body = render_template(
        'templates/documentation.pt',
        main_template = get_template('templates/main_template.pt'),
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response    

def community_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    body = render_template(
        'templates/community.pt',
        main_template = get_template('templates/main_template.pt'),
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response    

def software_view(context, request):
    response = webob.Response()
    app_url = request.application_url
    body = render_template(
        'templates/software.pt',
        main_template = get_template('templates/main_template.pt'),
        application_url = app_url,
        )
    response.unicode_body = unicode(body)
    return response    

