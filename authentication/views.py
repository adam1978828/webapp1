import json
import re
from urlparse import urlparse, parse_qs
from django.conf import settings
from django.core import mail
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from Model import User, UserRestorePassword
from django.utils import translation
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse


def login(request):
    translation.activate('uk')
    request.session[translation.LANGUAGE_SESSION_KEY] = 'uk'
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('profiles.views.view'))
    else:
        error = False
        if request.method == "POST":
            username = request.POST.get('login_name', u'')
            password = request.POST.get('login_pw', u'')
            user = auth.authenticate(username=username, password=password, user_type=[2, 3])
            if user is not None and user.is_active:
                auth.login(request, user)
            else:
                error = True
            if request.user.is_company:
                next_url = parse_qs(urlparse(request.META['HTTP_REFERER']).query).get(
                    'next', reverse('dashboard.views.all_charts'))
            else:
                next_url = parse_qs(urlparse(request.META['HTTP_REFERER']).query).get(
                    'next', reverse('profiles.views.view'))
            return HttpResponse(json.dumps({'error': error, 'next': next_url}),
                                content_type="application/json")
        return render_to_response('login.html', {'error': error},
                                  context_instance=RequestContext(request))


def restore(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('profiles.views.view'))
    else:
        message = ''
        if request.method == "POST":
            email = request.POST.get('email', '').strip().lower()
            if not email:
                message = _(u'Please, fill email field')
            elif not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]+$", email):
                message = _(u'Please, enter a valid email')
            else:
                user = request.db_session.query(User)\
                    .filter_by(email=email)\
                    .filter(User.user_type_id.in_([2, 3])).first()
                if user is not None and user.is_active:
                    urp = UserRestorePassword(user)
                    text = _(
                        u'Press this link and follow commands to restore your password: \n %(url)s')
                    url = 'http://%s/auth/restore/code/%s' % (
                        request.META['HTTP_HOST'], urp.change_pass_code)
                    mail.send_mail(_(u'Password restoring.'),
                                   text % {'url': url},
                                   settings.DEFAULT_FROM_EMAIL,
                                   [email],
                                   fail_silently=False)
                    request.db_session.add(urp)
                    request.db_session.commit()
                    # return HttpResponseRedirect("../acc/profile")
                else:
                    # In case of fail, returning mistake
                    message = _(u'This email is not registered')
            return HttpResponse(json.dumps({'error': message and True or False,
                                            'message': message}),
                                content_type="application/json")
        return render_to_response('restore.html', {'error': False},
                                  context_instance=RequestContext(request))


def restore_code(request, code):
    message = ''
    urp = request.db_session.query(UserRestorePassword)\
        .filter_by(change_pass_code=code)\
        .filter_by(dt_use=None)\
        .first()
    if not urp:
        return render_to_response('auth_404.html')
    if request.method == 'POST':
        password1 = request.POST.get('v1_password', '')
        password2 = request.POST.get('v1_repeat_password', '')
        if not password1:
            message = _(u'Please, enter valid password')
        elif password1 != password2:
            message = _(u'Your password does\'t match')
        else:
            urp.done(password1)
            message = urp.errors and urp.errors[0]['message']
        return HttpResponse(json.dumps({'error': message and True or False,
                                        'message': message}),
                            content_type="application/json")

    return render_to_response('restore_pass.html', {'error': message, 'email': urp.user.email},
                              context_instance=RequestContext(request))


def logout(request):
    if request.user.is_authenticated():
        auth.logout(request)
    return HttpResponseRedirect("/auth/login")


@require_POST
def ajax_check_credentials(request):
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=email, password=password, user_type=[2, 3])
    resp = {'error': not (user is not None and user.is_active)}
    return HttpResponse(json.dumps(resp), content_type="application/json")


@require_POST
def ajax_check_email(request):
    email = request.POST.get('email', '')
    user = request.db_session.query(User).filter_by(email=email).first()
    resp = {'error': not (user is not None and user.is_active)}
    return HttpResponse(json.dumps(resp), content_type="application/json")


@require_POST
def ajax_change_password(request):
    message = ''
    old_pass = request.POST.get('settings-old-password', '')
    new_pass = request.POST.get('settings-new-password', '')
    rep_pass = request.POST.get('settings-rep-password', '')
    if not request.user.is_pass_valid(old_pass):
        message = _(u'Wrong old password')
    elif len(new_pass) <= 4:
        message = _(u'Too short password')
    elif new_pass != rep_pass:
        message = _(u'Passwords doesn\'t match')
    else:
        request.user.set_password(new_pass)
    return HttpResponse(json.dumps({'error': message and True or False,
                                    'message': message}),
                        content_type="application/json")


def test(request):
    return render_to_response('test001.html',
                              context_instance=RequestContext(request))


def error404(request):
    return render_to_response('auth_404.html', {'message': ''},
                              context_instance=RequestContext(request))
