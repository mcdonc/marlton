from datetime import datetime
from persistent import Persistent

from zope.interface import implements
from repoze.bfg.interfaces import ILocation

from repoze.bfg.security import Allow
from repoze.bfg.security import Everyone
from repoze.bfg.security import Authenticated

from repoze.session.manager import SessionDataManager

from repoze.folder import Folder

from bfgsite.interfaces import IWebSite
from bfgsite.interfaces import IBin
from bfgsite.interfaces import IPasteBin
from bfgsite.interfaces import ITutorialBin
from bfgsite.interfaces import IPasteEntry
from bfgsite.interfaces import ITutorial
from bfgsite.interfaces import ISphinxDocument

from bfgsite.catalog import populate_catalog

class WebSite(Folder):
    implements(IWebSite, ILocation)
    __name__ = __parent__ = None
    __acl__ = [ (Allow, Everyone, 'view'), (Allow, Authenticated, 'manage') ]

    def __init__(self):
        super(WebSite, self).__init__()
        self['pastebin'] = PasteBin()
        self['tutorialbin'] = TutorialBin()
        self.sessions = SessionDataManager(3600, 5)

class Bin(Folder):
    implements(IBin)
    __acl__ = [ (Allow, Everyone, 'view'), (Allow, Authenticated, 'manage') ]

    current_id = -1

    def add(self, item):
        newid = self.current_id + 1
        self.current_id = newid
        itemid = str(newid)
        self[itemid] = item
        return itemid

class PasteBin(Bin):
    implements(IPasteBin)

class TutorialBin(Bin):
    implements(ITutorialBin)

class PasteEntry(Persistent):
    implements(IPasteEntry)

    def __init__(self, author_name, paste, language):
        self.author_name = author_name
        self.paste = paste
        self.language = language
        self.date = datetime.now()
        
class Tutorial(Persistent):
    implements(ITutorial)

    def __init__(self, title, author_name, text, author_url=None, code=None,
                 language=None):
        self.title = title
        self.author_name = author_name
        self.author_url = author_url
        self.text = text
        self.code = code
        self.language = language
        self.date = datetime.now()

class SphinxDocument: # not persistent!
    implements(ISphinxDocument)
    def __init__(self, text):
        self.text = text
        self.modified = datetime.now()
        self.created = datetime.now()

def appmaker(root):
    if not root.has_key('bfgsite'):
        website = WebSite()
        root['bfgsite'] = website
        populate_catalog(website)
        import transaction
        transaction.commit()
    return root['bfgsite']

def NonPersistentRootFinder(db_path):
    site = WebSite()
    def get_root(environ):
        return site
    return get_root

