from random import choice
import urlparse

from zope.component import getUtility

from pygments import formatters
from pygments import lexers

from pyramid.renderers import get_renderer

from pyramid.traversal import find_interface
from pyramid.security import authenticated_userid
from pyramid.url import resource_url

from repoze.sendmail.interfaces import IMailDelivery

from marlton.interfaces import IWebSite
from marlton.interfaces import IPasteBin
from marlton.interfaces import IPasteEntry
from marlton.interfaces import ITutorialBin
from marlton.interfaces import ITutorial

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

def preferred_author(context, request):
    author_name = request.params.get('author_name', u'')
    if not author_name:
        author_name = request.cookies.get(COOKIE_AUTHOR, u'')
        if not author_name:
            userid = authenticated_userid(request)
            profiles = find_profiles(context)
            if profiles is not None:
                profile = profiles.get(userid)
                author_name = getattr(profile, 'fullname', u'')
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
         'view_name':'',
         'title':'Home'},
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite,),
         'view_name':'book',
         'title':'Book'},
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite,),
         'view_name':'documentation',
         'title':'Docs'},
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
        self.context_url = resource_url(context, request)
        self.site = find_interface(context, IWebSite)
        self.request = request
        self.application_url = request.application_url
        self.userid = authenticated_userid(request)
        self.is_home_page = request.url == request.application_url + '/'
        profile = None
        profiles = find_profiles(context)
        if profiles is not None:
            profile = profiles.get(self.userid)
            self.fullname = getattr(profile, 'fullname', None)
        if profile:
            self.profile_edit_url = resource_url(profile, request, 'edit')
        else:
            self.profile_edit_url = None

    @property
    def main_template(self):
        if self.is_home_page:
            return get_renderer(
                'views/templates/frontpage_main_template.pt').implementation()
        return get_renderer('views/templates/main_template.pt').implementation()

    @property
    def navitems(self):
        items = get_navigation(self.context, self.request, self.nav_links)
        logged_in = authenticated_userid(self.request)
        if logged_in:
            items.extend(
                get_navigation(self.context, self.request,
                               [{'view_iface':IWebSite,
                                'nav_ifaces':(IWebSite,),
                                'view_name':'logout',
                                'title':'Log Out'}])
                )
        else:
            items.extend(
                get_navigation(self.context, self.request,
                               [{'view_iface':IWebSite,
                                'nav_ifaces':(IWebSite,),
                                'view_name':'login',
                                'title':'Log In'}])
                )
        return items
        

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
                 'href':resource_url(viewcontext, request, view_name),
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

def find_users(context):
    site = find_site(context)
    if site is None:
        return None
    return site.users

def find_profiles(context):
    site = find_site(context)
    if site is None:
        return None
    return site['profiles']

def find_site(context):
    return find_interface(context, IWebSite)

def random_password():
    friendly = ''.join(
        [choice('bcdfghklmnprstvw')+choice('aeiou') for i in range(4)])
    return friendly

class All(object):
    def __call__(self, other):
        return self

    def __contains__(self, other):
        return True

def get_tutorials(context, request, max):
    tutorialbin = find_interface(context, ITutorialBin)
    tutorials = []
    keys = sort_byint(tutorialbin.keys())
    keys = keys[:max]
    for name in keys:
        tutorial = tutorialbin[name]
        if tutorial.date is not None:
            pdate = tutorial.date.strftime('%x')
        else:
            pdate = 'UNKNOWN'
        tutorial_url = resource_url(tutorial, request)
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

def get_pastes(context, request, max):
    pastebin = find_interface(context, IPasteBin)
    pastes = []
    pastebin_url = resource_url(pastebin, request)
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

def get_mailer():
    mailer = getUtility(IMailDelivery)
    return mailer

    
