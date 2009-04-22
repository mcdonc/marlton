from StringIO import StringIO

from webob import Response

from Captcha.Visual.Tests import PseudoGimpy

from bfgsite.utils import find_site

from repoze.bfg.view import bfg_view

@bfg_view(name='captcha.jpg')
def captcha_jpeg(context, request):
    site = find_site(context)
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

