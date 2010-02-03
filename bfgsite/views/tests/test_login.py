import unittest

from repoze.bfg import testing

class Test_logout_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.login import logout_view
        return logout_view(context, request)

    def test_it(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        
class Test_login_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.login import login_view
        return login_view(context, request)

    def test_notsubmitted(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.assertEqual(result['login'], '')
        self.assertEqual(result['password'], '')
        self.failIf(result['logged_in'])
        
        
