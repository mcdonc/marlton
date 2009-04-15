from zope.interface import implements

from repoze.bfg.url import model_url

from bfgsite.interfaces import ISearchText
from bfgsite.interfaces import IBatchInfo

class TutorialSearchTextAdapter(object):
    implements(ISearchText)
    def __init__(self, context):
        self.context = context

    def __call__(self):
        strings = []
        context = self.context
        for attr in ('title', 'author_name', 'text', 'author_url', 'code',
                     'language'):
            val = getattr(context, attr, None)
            if val is not None:
                strings.append(val)
        return ' '.join(strings)
    
class TutorialBatchInfoAdapter(object):
    implements(IBatchInfo)
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {'type':'Tutorial', 'title':self.context.title,
                'url':model_url(self.context, self.request)}
        
class PasteEntrySearchTextAdapter(object):
    implements(ISearchText)
    def __init__(self, context):
        self.context = context

    def __call__(self):
        strings = []
        context = self.context
        for attr in ('author_name', 'paste', 'language'):
            val = getattr(context, attr, None)
            if val is not None:
                strings.append(val)
        return ' '.join(strings)

class PasteEntryBatchInfoAdapter(object):
    implements(IBatchInfo)
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return {
            'type':'Paste Entry',
            'title':'%s %s...' % (self.context.author_name,
                                  self.context.paste[:100]),
            'url':model_url(self.context, self.request)
            }
