from datetime import datetime
from persistent import Persistent
from ZODB.blob import Blob
import transaction

from zope.interface import implements

from repoze.bfg.interfaces import ILocation
from repoze.bfg.security import Allow
from repoze.bfg.security import Everyone

from repoze.who.plugins.zodb.users import Users

from repoze.session.manager import SessionDataManager

from repoze.folder import Folder

from bfgsite.interfaces import IWebSite
from bfgsite.interfaces import IBin
from bfgsite.interfaces import IPasteBin
from bfgsite.interfaces import ITutorialBin
from bfgsite.interfaces import IPasteEntry
from bfgsite.interfaces import ITutorial
from bfgsite.interfaces import ISphinxDocument
from bfgsite.interfaces import IProfile
from bfgsite.interfaces import IProfiles

from bfgsite.catalog import populate_catalog

class WebSite(Folder):
    implements(IWebSite, ILocation)
    __name__ = __parent__ = None
    __acl__ = [ (Allow, Everyone, 'view'), (Allow, 'admin', 'manage') ]

    def __init__(self):
        super(WebSite, self).__init__()
        self['pastebin'] = PasteBin()
        self['tutorialbin'] = TutorialBin()
        self.sessions = SessionDataManager(3600, 5)

class Bin(Folder):
    implements(IBin)
    __acl__ = [ (Allow, Everyone, 'view'), (Allow, 'members', 'add'),
                (Allow, 'admin', ('manage', 'add')) ]

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

    def __init__(self, title, author_name, text, url=None, code=None,
                 language=None, stream=None, file_name=None, mime_type=None):
        self.title = title
        self.author_name = author_name
        self.url = url
        self.text = text
        self.code = code
        self.language = language
        self.date = datetime.now()
        self.attachment_data = Blob()
        self.attachment_name = file_name
        self.attachment_mimetype = mime_type
        self.upload(stream)
        
    def upload(self, stream):
        if stream is not None:
            f = self.attachment_data.open('w')
            size = save_data(stream, f)
            f.close()
            self.attachment_size = size        

class SphinxDocument: # not persistent!
    implements(ISphinxDocument)
    def __init__(self, text):
        self.text = text
        self.modified = datetime.now()
        self.created = datetime.now()

class Profile(Persistent):
    implements(IProfile)
    def __init__(self, fullname, email):
        self.fullname = fullname
        self.email = email

class Profiles(Folder):
    implements(IProfiles)
    
def file_buffer(stream, chunk_size=10000):
    while True:
        chunk = stream.read(chunk_size)
        if not chunk: break
        yield chunk    
        
def save_data(stream, file):
    size = 0
    for chunk in file_buffer(stream):
        size += len(chunk)        
        file.write(chunk)
    return size        

def appmaker(root):
    if not root.has_key('bfgsite'):
        website = WebSite()
        root['bfgsite'] = website
        populate_catalog(website)
        profiles = Profiles()
        profiles['admin'] = Profile('Ad Min', 'admin@example.com')
        website['profiles'] = profiles
        users = Users()
        users.add('admin', 'admin', 'admin', groups=('admin',))
        website.users = users
        transaction.commit()
    return root['bfgsite']

def find_users_via_root(root):
    return root['bfgsite'].users

