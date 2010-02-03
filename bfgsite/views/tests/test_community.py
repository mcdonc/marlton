import unittest

from repoze.bfg import testing

class Test_community_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.community import community_view
        return community_view(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.failUnless('api' in result)
        
        
        
