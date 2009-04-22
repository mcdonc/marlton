import formencode
from email.Message import Message

from webob.exc import HTTPFound

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.view import bfg_view
from repoze.bfg.security import authenticated_userid
from repoze.bfg.security import Allow
from repoze.bfg.url import model_url

from bfgsite.interfaces import IWebSite
from bfgsite.interfaces import IProfile

from bfgsite.models import Profile
from bfgsite.utils import API
from bfgsite.utils import find_users
from bfgsite.utils import find_profiles
from bfgsite.utils import get_security_policy
from bfgsite.utils import random_password
from bfgsite.utils import get_mailer

@bfg_view(for_=IWebSite, name='register', permission='view')
def register_view(context, request):
    logged_in = authenticated_userid(request)
    login = request.params.get('login', '')
    fullname = request.params.get('fullname', '')
    email = request.params.get('email', '')
    password = request.params.get('password', '')
    password_verify = request.params.get('password_verify')
    captcha_answer = request.params.get('captcha_answer', '')
    message = ''

    if 'form.submitted' in request.params:
        schema = RegisterSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            ok = False
            session = context.sessions.get(request.environ['repoze.browserid'])
            solutions = session.get('captcha_solutions', [])
            for solution in solutions:
                if captcha_answer.lower() == solution.lower():
                    ok = True
            if not ok:
                message = 'Bad CAPTCHA answer'
            else:
                users = find_users(context)
                info = users.get_by_login(login)
                if info:
                    message = 'Username %s already exists' % login
                else:
                    if password != password_verify:
                        message = 'Password and password verify do not match'
                    else:
                        users.add(login, login, password, groups=('members',))
                        profiles = find_profiles(context)
                        profile = Profile(fullname, email)
                        profiles[login] = profile
                        acl = context.__acl__[:]
                        acl.extend([(Allow, login, 'edit'),
                                    (Allow, 'admin', 'edit')])
                        profile.__acl__ = acl
                        identity = {}
                        identity['repoze.who.userid'] = login
                        policy = get_security_policy()
                        headers = policy.auth.forget(request.environ, None)
                        headers = policy.auth.remember(request.environ,
                                                       identity)
                        login_url = model_url(context, request, 'login')
                        response = HTTPFound(location = login_url,
                                             headers=headers)
                        return response
        
    return render_template_to_response(
        'templates/register.pt',
        api = API(context, request),
        logged_in = logged_in,
        message = message,
        email = email,
        login = login,
        fullname = fullname,
        password = password,
        password_verify = password_verify,
        captcha_answer = captcha_answer,
        )

@bfg_view(for_=IProfile, name='edit', permission='edit')
def profile_edit_view(context, request):
    login = authenticated_userid(request)
    fullname = context.fullname
    email = context.email
    password = ''
    password_verify = ''
    message = ''

    if 'form.editprofile' in request.params:
        schema = ProfileSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            fullname = request.params['fullname']
            email = request.params['email']
            profiles = find_profiles(context)
            profile = profiles[login]
            profile.fullname = fullname
            profile.email = email
            message = 'Profile edited'

    if 'form.changepassword' in request.params:
        schema = ChangePasswordSchema()
        message = None
        try:
            form = schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            password = request.params['password']
            password_verify = request.params['password_verify']
            if password != password_verify:
                message = 'Password and password verify do not match'
            else:
                users = find_users(context)
                users.change_password(login, password)
                message = 'Password changed'
        
    return render_template_to_response(
        'templates/profile_edit.pt',
        api = API(context, request),
        login = login,
        message = message,
        email = email,
        fullname = fullname,
        password = password,
        password_verify = password_verify,
        )

@bfg_view(for_=IWebSite, name='forgot_password', permission='view')
def forgot_password_view(context, request):
    email = request.params.get('email', '')
    message = ''
    if 'form.submitted' in request.params:
        schema = ForgotPasswordSchema()
        try:
            schema.to_python(request.params)
        except formencode.validators.Invalid, why:
            message = str(why)
        else:
            profiles = find_profiles(context)
            found_profile = None
            for profile in profiles.values():
                if profile.email == email:
                    found_profile = profile
                    break
            if found_profile is None:
                message = 'Email %s not found' % email
            else:
                login = profile.__name__
                password = random_password()
                users = find_users(context)
                users.change_password(login, password)
                msg = Message()
                frm = 'bfg.repoze.org <donotreply@repoze.org>'
                msg['From'] = frm
                msg['To'] = email
                msg['Subject'] = 'Account information'
                body = 'Your new password is "%s" for login name "%s"' % (
                    password, login)
                msg.set_payload(body)
                msg.set_type('text/html')
                message = msg.as_string()
                mailer = get_mailer()
                mailer.send(frm, [email], message)
                message = 'Mail sent to "%s" with new password' % email

    return render_template_to_response(
        'templates/forgot_password.pt',
        api = API(context, request),
        email=email,
        message=message,
        )

class ProfileSchema(formencode.Schema):
    allow_extra_fields = True
    fullname = formencode.validators.NotEmpty()
    email = formencode.validators.Email(not_empty=True)

class RegisterSchema(ProfileSchema):
    login = formencode.validators.NotEmpty()
    password = formencode.validators.NotEmpty()
    password_verify = formencode.validators.NotEmpty()
    captcha_answer = formencode.validators.NotEmpty()

class ForgotPasswordSchema(formencode.Schema):
    allow_extra_fields = True
    email = formencode.validators.Email(not_empty=True)

class ChangePasswordSchema(formencode.Schema):
    allow_extra_fields = True
    password = formencode.validators.NotEmpty()
    password_verify = formencode.validators.NotEmpty()

