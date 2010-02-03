import unittest

from repoze.bfg import testing

class Test_docs_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.favicon import favicon_view
        return favicon_view(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.content_type, 'image/x-icon')
        
        
        
        
