from StringIO import StringIO
from Captcha.Visual.Tests import PseudoGimpy
from webob import Response

from repoze.bfg.view import bfg_view
from bfgsite.utils import find_site

@bfg_view(name='captcha.jpg')
def captcha_jpeg(context, request):
    site = find_site(context)
    output = StringIO()
    
    captcha = PseudoGimpy()
    image = captcha.render()
    image.save(output, 'JPEG')
    data = output.getvalue()
    browserid = request.environ.get('repoze.browserid')
    session = site.sessions.get(browserid)
    session['captcha_solutions'] = captcha.solutions
    r = Response(data, '200 OK', [ ('Content-Type', 'image/jpeg'),
                                   ('Content-Length', len(data)) ])
    return r

