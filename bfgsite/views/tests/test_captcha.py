import unittest

from repoze.bfg import testing

class Test_captcha_jpeg(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.captcha import captcha_jpeg
        return captcha_jpeg(context, request)

    def test_it(self):
        from bfgsite.interfaces import IWebSite
        request = testing.DummyRequest()
        context = testing.DummyModel(__provides__=IWebSite)
        context.sessions = {None:{}}
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'image/jpeg')
        self.assertEqual(len(context.sessions[None]), 1)
        
        
