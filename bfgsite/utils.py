from pygments import formatters
from pygments import lexers

from repoze.bfg.chameleon_zpt import get_template

from repoze.bfg.traversal import find_interface

from repoze.bfg.url import model_url

from bfgsite.interfaces import IWebSite
from bfgsite.interfaces import IPasteBin
from bfgsite.interfaces import IPasteEntry
from bfgsite.interfaces import ITutorialBin
from bfgsite.interfaces import ITutorial


COOKIE_LANGUAGE = 'website.last_lang'
COOKIE_AUTHOR = 'website.last_author'

def sort_byint(keys):
    """Sort a list of integer id keys in reverse order"""
    keys = list(keys)
    def byint(a, b):
        try:
            return cmp(int(a), int(b))
        except TypeError:
            return cmp(a, b)
    keys.sort(byint)
    keys.reverse()
    return keys

def preferred_author(request):
    author_name = request.params.get('author_name', u'')
    if not author_name:
        author_name = request.cookies.get(COOKIE_AUTHOR, u'')
    if isinstance(author_name, str):
        author_name = unicode(author_name, 'utf-8')
    return author_name

def nl_to_br(s):
    s = s.replace('\n', '<br>')
    return s


class API:
    nav_links = (
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite),
         'view_name':'searchresults',
         'title':'Search'},
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite,),
         'view_name':'documentation',
         'title':'Docs'},
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite,),
         'view_name':'trac',
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

formatter = formatters.HtmlFormatter(linenos=True,
                                     cssclass="source")
style_defs = formatter.get_style_defs()

all_lexers = list(lexers.get_all_lexers())
all_lexers.sort()
lexer_info = []
for name, aliases, filetypes, mimetypes_ in all_lexers:
    lexer_info.append({'alias':aliases[0], 'name':name})

