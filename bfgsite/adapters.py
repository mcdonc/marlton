from zope.interface import implements
from repoze.bfg.url import model_url
from repoze.bfg.traversal import find_interface
from bfgsite.interfaces import INavigation
from bfgsite.interfaces import IWebSite

class DefaultNavigation(object):

    implements(INavigation)
    links = (
        {'context_iface':IWebSite,
         'view_name':'',
         'title':'Home'},
        {'context_iface':IWebSite,
         'view_name':'documentation',
         'title':'Documentation'},
        {'context_iface':IWebSite,
         'view_name':'software',
         'title':'Software'},
        {'context_iface':IWebSite,
         'view_name':'community',
         'title':'Community'},
        {'context_iface':IWebSite,
         'view_name':'pastebin',
         'title':'Paste Bin'},
        )

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def items(self):
        items = []

        for link in self.links:
            if self.request.view_name == link['view_name']:
                state = 'current'
            else:
                state = 'notcurrent'

            navcontext = find_interface(self.context, link['context_iface'])

            items.append(
                {'state':state,
                 'href':model_url(navcontext, self.request,
                                  link['view_name']),
                 'title':link['title'],
                 })
        
        return items

    
