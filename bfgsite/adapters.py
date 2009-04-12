from zope.interface import implements
from repoze.bfg.url import model_url
from repoze.bfg.traversal import find_interface
from bfgsite.interfaces import INavigation
from bfgsite.interfaces import IWebSite
from bfgsite.interfaces import IPasteBin
from bfgsite.interfaces import IPasteEntry
from bfgsite.interfaces import ITutorialBin
from bfgsite.interfaces import ITutorial

class DefaultNavigation(object):

    implements(INavigation)
    links = (
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite,),
         'view_name':'documentation',
         'title':'Documentation'},
        {'view_iface':IWebSite,
         'nav_ifaces':(IWebSite,),
         'view_name':'software',
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
        self.request = request
        
    def items(self):
        items = []

        for link in self.links:
            state = 'notcurrent'
            view_iface = link['view_iface']
            nav_ifaces = link['nav_ifaces']
            view_name = link['view_name']

            if view_iface.providedBy(self.context):
                if self.request.view_name == view_name:
                    state = 'current'
            else:
                for nav_iface in nav_ifaces:
                    if nav_iface.providedBy(self.context):
                        state = 'current'
                        break

            viewcontext = find_interface(self.context, view_iface)

            items.append(
                {'state':state,
                 'href':model_url(viewcontext, self.request, view_name),
                 'title':link['title'],
                 })

        return items

    
