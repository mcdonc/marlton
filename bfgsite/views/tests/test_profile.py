import unittest

from repoze.bfg import testing

class Test_register_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.profile import register_view
        return register_view(context, request)

    def test_notsubmitted(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.failUnless('api' in result)
        

class Test_profile_edit_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.profile import profile_edit_view
        return profile_edit_view(context, request)

    def test_notsubmitted(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        context.fullname = 'fullname'
        context.email = 'email'
        result = self._callFUT(context, request)
        self.failUnless('api' in result)
        
class Test_forgot_password_view(unittest.TestCase):
    def _callFUT(self, context, request):
        from bfgsite.views.profile import forgot_password_view
        return forgot_password_view(context, request)

    def test_notsubmitted(self):
        request = testing.DummyRequest()
        context = testing.DummyModel()
        result = self._callFUT(context, request)
        self.failUnless('api' in result)
        
