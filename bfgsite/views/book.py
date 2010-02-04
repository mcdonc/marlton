import os
from docutils.core import publish_parts
from repoze.bfg.view import bfg_view

from bfgsite.interfaces import IWebSite
from bfgsite.utils import API

here = os.path.dirname(os.path.abspath(__file__))
errata_rst = open(os.path.join(here, 'book_errata.rst')).read()

@bfg_view(for_=IWebSite, name='book', permission='view',
          renderer='bfgsite.views:templates/book.pt')
def book_view(context, request):
    return {'api':API(context, request)}

@bfg_view(for_=IWebSite, name='book_errata', permission='view',
          renderer='bfgsite.views:templates/errata.pt')
def errata_view(context, request):
    content = publish_parts(errata_rst, writer_name='html')['html_body']
    return {'api':API(context, request), 'errata':content}


    
    
