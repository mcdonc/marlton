import unittest

from repoze.bfg import testing

class Test_index_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.index import index_view
        return index_view(context, request)

    def test_it(self):
        from bfgsite.interfaces import ITutorialBin
        request = testing.DummyRequest()
        context = testing.DummyModel()
        context['tutorialbin'] = testing.DummyModel(__provides__=ITutorialBin)
        result = self._callFUT(context, request)
        self.failUnless('api' in result)
        self.failUnless('tutorials' in result)
        
class Test_robots_txt(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.index import robots_txt
        return robots_txt(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.content_type, 'text/plain')
        
        
        
        
