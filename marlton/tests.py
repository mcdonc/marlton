import unittest

class WebSiteModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from models import WebSite
        return WebSite

    def _makeOne(self):
        return self._getTargetClass()()

    def test_constructor(self):
        from models import PasteBin
        from models import TutorialBin
        from repoze.session.manager import SessionDataManager
        from pyramid.security import Allow
        from pyramid.security import Everyone
        website = self._makeOne()
        acl = [ (Allow, Everyone, 'view'), (Allow, 'admin', 'manage') ]
        self.assertEqual(website.__parent__, None)
        self.assertEqual(website.__name__, None)
        self.assertEqual(website.__acl__, acl)
        self.assertEqual(website['pastebin'].__class__, PasteBin)
        self.assertEqual(website['tutorialbin'].__class__, TutorialBin)
        self.assertEqual(website.sessions.__class__, SessionDataManager)

class PasteBinModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from models import PasteBin
        return PasteBin

    def _makeOne(self):
        return self._getTargetClass()()

    def test_constructor(self):
        from pyramid.security import Allow
        from pyramid.security import Everyone
        pastebin = self._makeOne()
        acl = [ (Allow, Everyone, 'view'), (Allow, 'members', 'add'),
                (Allow, 'admin', ('manage', 'add')) ]
        self.assertEqual(pastebin.current_id, -1)
        self.assertEqual(pastebin.__acl__, acl)

class TutorialBinModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from models import TutorialBin
        return TutorialBin

    def _makeOne(self):
        return self._getTargetClass()()

    def test_constructor(self):
        from pyramid.security import Allow
        from pyramid.security import Everyone
        tutorialbin = self._makeOne()
        acl = [ (Allow, Everyone, 'view'), (Allow, 'members', 'add'),
                (Allow, 'admin', ('manage', 'add')) ]
        self.assertEqual(tutorialbin.current_id, -1)
        self.assertEqual(tutorialbin.__acl__, acl)

class PasteEntryModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from models import PasteEntry
        return PasteEntry

    def _makeOne(self, author_name=u'johny', paste=u'print "hello world!"\n',
                 language=u'Python'):
        return self._getTargetClass()(author_name=author_name, paste=paste,
                                      language=language)

    def test_constructor(self):
        pasteentry = self._makeOne()
        self.assertEqual(pasteentry.author_name, u'johny')
        self.assertEqual(pasteentry.paste, u'print "hello world!"\n')
        self.assertEqual(pasteentry.language, u'Python')

class TutorialModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from models import Tutorial
        return Tutorial

    def _makeOne(self, title=u'How to test', author_name=u'johny',
                 url=u'http://bfg.repoze.org/testing', text=u'Just do it!',
                 code=u'import unittest\nclass Test(unittest.TestCase):\n',
                 language=u'Python'):
        return self._getTargetClass()(title=title, author_name=author_name,
                                      text=text, url=url, code=code,
                                      language=language)

    def test_constructor(self):
        from ZODB.blob import Blob
        tutorial = self._makeOne()
        self.assertEqual(tutorial.title, u'How to test')
        self.assertEqual(tutorial.author_name, u'johny')
        self.assertEqual(tutorial.url, u'http://bfg.repoze.org/testing')
        self.assertEqual(tutorial.text, u'Just do it!')
        self.assertEqual(tutorial.code,
                u'import unittest\nclass Test(unittest.TestCase):\n')
        self.assertEqual(tutorial.language, u'Python')
        self.assertEqual(tutorial.attachment_data.__class__, Blob)
        self.assertEqual(tutorial.attachment_name, None)
        self.assertEqual(tutorial.attachment_mimetype, None)

class ProfileModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from models import Profile
        return Profile

    def _makeOne(self, fullname='johny q.', email='johny@example.com'):
        return self._getTargetClass()(fullname=fullname, email=email)

    def test_constructor(self):
        profile = self._makeOne()
        self.assertEqual(profile.fullname, 'johny q.')
        self.assertEqual(profile.email, 'johny@example.com')

class SphinxDocumentModelTests(unittest.TestCase):

    def _getTargetClass(self):
        from models import SphinxDocument
        return SphinxDocument

    def _makeOne(self, text=u'This is a document'):
        return self._getTargetClass()(text=text)

    def test_constructor(self):
        sphinxdocument = self._makeOne()
        self.assertEqual(sphinxdocument.text, u'This is a document')

class AppmakerTests(unittest.TestCase):

    def _callFUT(self, zodb_root):
        from models import appmaker
        return appmaker(zodb_root)

    def test_no_app_root(self):
        from repoze.who.plugins.zodb.users import Users
        root = {}
        self._callFUT(root)
        self.assertEqual(root['marlton']['profiles']['admin'].fullname,
                         'Ad Min')
        self.assertEqual(root['marlton']['profiles']['admin'].email,
                         'admin@example.com')
        self.assertEqual(root['marlton'].users.__class__, Users)

    def test_w_app_root(self):
        app_root = object()
        root = {'app_root': app_root}
        self._callFUT(root)
        self.failUnless(root['app_root'] is app_root)

