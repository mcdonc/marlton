import os
from docutils.core import publish_parts
from pyramid.view import view_config

from marlton.interfaces import IWebSite
from marlton.utils import API

here = os.path.dirname(os.path.abspath(__file__))
errata_rst = open(os.path.join(here, 'book_errata.rst')).read()

@view_config(for_=IWebSite, name='book', permission='view',
             renderer='marlton.views:templates/book.pt')
def book_view(context, request):
    return {'api':API(context, request)}

@view_config(for_=IWebSite, name='book_errata', permission='view',
             renderer='marlton.views:templates/errata.pt')
def errata_view(context, request):
    content = publish_parts(errata_rst, writer_name='html')['html_body']
    return {'api':API(context, request), 'errata':content}


    
    
