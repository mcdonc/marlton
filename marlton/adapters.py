from zope.interface import implements

from marlton.interfaces import ISearchText
from marlton.interfaces import IMetadata

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
    
class TutorialMetadataAdapter(object):
    implements(IMetadata)
    def __init__(self, context):
        self.context = context

    def __call__(self):
        return {
            'type':'Tutorial',
            'title':self.context.title,
            'teaser':self.context.text[:300]
            }
    
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

class PasteEntryMetadataAdapter(object):
    implements(IMetadata)
    def __init__(self, context):
        self.context = context

    def __call__(self):
        return {
            'type':'Paste Entry',
            'title':'Paste Entry by %s' % self.context.author_name,
            'teaser':self.context.paste[:300],
            }

class SphinxDocumentSearchTextAdapter(object):
    implements(ISearchText)
    def __init__(self, context):
        self.context = context

    def __call__(self):
        return self.context.text
