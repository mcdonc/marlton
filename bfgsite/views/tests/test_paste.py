import unittest

from repoze.bfg import testing

class Test_entry_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.paste import entry_view
        return entry_view(context, request)

    def test_it(self):
        import datetime
        from bfgsite.interfaces import IPasteBin
        request = testing.DummyRequest()
        context = testing.DummyModel(__provides__=IPasteBin)
        context.paste = 'text'
        context.language = 'en'
        context.author_name = 'abc'
        context.date = datetime.date.today()
        result = self._callFUT(context, request)
        self.failUnless('api' in result)
        self.assertEqual(result['author'], 'abc')
        self.assertEqual(result['date'], context.date.strftime('%x at %X'))
        self.assertEqual(result['pastes'], [])
        
class Test_pastebin_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.paste import pastebin_view
        return pastebin_view(context, request)

    def test_notsubmitted(self):
        from bfgsite.interfaces import IPasteBin
        request = testing.DummyRequest()
        context = testing.DummyModel(__provides__=IPasteBin)
        result = self._callFUT(context, request)
        self.failUnless('api' in result)

class Test_pastebin_manage_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.paste import pastebin_manage_view
        return pastebin_manage_view(context, request)

    def test_notsubmitted(self):
        from bfgsite.interfaces import IPasteBin
        request = testing.DummyRequest()
        context = testing.DummyModel(__provides__=IPasteBin)
        result = self._callFUT(context, request)
        self.failUnless('api' in result)
    
class Test_pastebin_rss_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.paste import pastebin_rss_view
        return pastebin_rss_view(context, request)

    def test_notsubmitted(self):
        from bfgsite.interfaces import IPasteBin
        request = testing.DummyRequest()
        context = testing.DummyModel(__provides__=IPasteBin)
        result = self._callFUT(context, request)
        self.failUnless('pastes' in result)
        self.assertEqual(request.response_content_type, 'application/rss+xml')
