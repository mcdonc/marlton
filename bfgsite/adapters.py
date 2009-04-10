from zope.interface import implements
from repoze.bfg.url import model_url
from bfgsite.interfaces import INavigation

class Navigation:
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
            items.append(
                {'state':state,
                 'href':model_url(self.context, self.request,
                                  link['view_name']),
                 'title':link['title'],
                 })
        
        return items

class WebSiteNavigation(Navigation):
    implements(INavigation)
    links = (
        {'view_name':'',
         'title':'Home'},
        {'view_name':'documentation',
         'title':'Documentation'},
        {'view_name':'software',
         'title':'Software'},
        {'view_name':'community',
         'title':'Community'},
        )

    
