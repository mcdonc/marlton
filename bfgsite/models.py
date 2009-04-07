from datetime import datetime
from persistent.mapping import PersistentMapping
from persistent import Persistent

from zope.interface import Interface
from zope.interface import implements
from repoze.bfg.interfaces import ILocation

from repoze.bfg.security import Allow
from repoze.bfg.security import Everyone
from repoze.bfg.security import Authenticated

class IWebSite(Interface):
    pass

class WebSite(PersistentMapping):
    implements(IWebSite, ILocation)
    __acl__ = [ (Allow, Everyone, 'view') ]

    def __init__(self):
        super(WebSite, self).__init__(self)
        self.__name__ = None
        self.__parent__ = None
        self['pastebin']=PasteBin()
        self['tutorialbin']=TutorialBin()

class IBin(Interface):
    pass

class Bin(PersistentMapping):
    implements(IBin)
    __acl__ = [ (Allow, Everyone, 'view'), (Allow, Authenticated, 'manage') ]

    current_id = -1

    def add(self, item):
        newid = self.current_id + 1
        self.current_id = newid
        itemid = str(newid)
        self[itemid] = item
        return itemid

class IPasteBin(Interface):
    pass

class PasteBin(Bin):
    implements(IPasteBin)

class ITutorialBin(Interface):
    pass

class TutorialBin(Bin):
    implements(ITutorialBin)

class IPasteEntry(Interface):
    pass

class PasteEntry(Persistent):
    implements(IPasteEntry)

    def __init__(self, author_name, paste, language):
        self.author_name = author_name
        self.paste = paste
        self.language = language
        self.date = datetime.now()
        
class ITutorial(Interface):
    pass

class Tutorial(Persistent):
    implements(ITutorial)

    def __init__(self, title, author_name, text, author_url=None, code=None, language=None):
        self.title = title
        self.author_name = author_name
        self.author_url = author_url
        self.text = text
        self.code = code
        self.language = language
        self.date = datetime.now()
        
def appmaker(root):
    if not root.has_key('bfgsite'):
        root['bfgsite'] = WebSite()
        import transaction
        transaction.commit()
    return root['bfgsite']

def NonPersistentRootFinder(db_path):
    site = WebSite()
    def get_root(environ):
        return site
    return get_root

