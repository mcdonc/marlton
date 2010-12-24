import unittest

from pyramid import testing

class Test_docs_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from marlton.views.docs import docs_view
        return docs_view(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.failUnless('api' in result)
        
        
        
