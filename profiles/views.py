# -*- coding: utf-8 -*-
import pytz

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from sqlalchemy.orm.exc import NoResultFound
from Model import User, SysObject, Group, SysFunction, Company, DiskOut30DaysView, Income30DaysView
from WebApp.utils import random_string
from WebApp.validators import email_valid, password_valid
from acc.decorators import permission_required
from acc.shortcuts import address_from_request, phone_number_from_request, address_from_request_for_profile
from django.core.urlresolvers import reverse

from libs.validators.core import json_response_content

__author__ = 'D.Ivanets, D.Kalpakchi'


@login_required()
def view(request):
    return render_to_response('profile.html', {'person': request.user},
                              context_instance=RequestContext(request))

# import pytz
# from django.shortcuts import redirect, render
#
# def set_timezone(request):
#     print 'set_timezone'
#     if request.method == 'POST':
#         request.session['django_timezone'] = request.POST['timezone']
#         return redirect('/')
#     else:
#         return render(request, 'template.html', {'timezones': pytz.common_timezones})

@login_required
@permission_required('user_view')
def view_by_id(request, user_id):
    try:
        person = request.db_session.query(User)\
            .filter_by(id=user_id)\
            .filter_by(company=request.user.company)\
            .one()

        Income30DaysView
    except:
        raise Http404
    return render_to_response('profile.html', {'person': person},
                              context_instance=RequestContext(request))


@login_required
@permission_required('user_add')
def add_staff(request):
    if request.POST:
        p = request.POST
        email = request.POST.get('i_email', '')
        password = request.POST.get('i_pass', random_string(8))
        user = User()
        if request.db_session.query(User)\
                .filter_by(email=email)\
                .filter_by(user_type_id=request.user.user_type_id).first():
            user.errors.append(
                {'field': 'email', 'message': 'User with such email already exists.'})

        if user.no_errors():
            user.email = email
            # here encryption is made in validator if validation is passed
            user.set_password(password)
            user.first_name = p.get('i_first_name', '')
            user.last_name = p.get('i_last_name', '')
            user.phone = phone_number_from_request(request.POST, 'i_phone')
            user.m_phone = phone_number_from_request(request.POST, 'i_m_phone')
            user.user_type = request.user.user_type

            if request.user.is_focus:
                company_id = request.POST.get('f_company_name', '')
                if company_id != "0":
                    user.company = request.db_session.query(Company).filter_by(id=company_id).first()
                    user.user_type_id = 2
            else:
                user.company = request.user.company

            user.local_tz = request.POST.get('f_tz', None)

            address = address_from_request(request.POST)

            if user.no_errors() and address.no_errors():
                request.db_session.add_all([user, address])
                user.address = address
                mail.send_mail('Account registration',
                               'Welcome to %s \n'
                               'Your registration information: \n'
                               'Email: %s\n'
                               'Password: %s\n' % (
                                   request.META['HTTP_HOST'], email, password),
                               settings.DEFAULT_FROM_EMAIL,
                               [email],
                               fail_silently=False)
                request.db_session.commit()
                # return HttpResponseRedirect(reverse('profiles.views.perms_by_id', args=(user.id,)))
                response = json_response_content('success', 'New worker was added successfully')
                response['redirect_url'] = reverse('profiles.views.perms_by_id', args=(user.id,))
            else:
                request.db_session.rollback()
                response = json_response_content('error', 'Some error occured during user creation')
                for error in user.errors:
                    response['errors'].append(error)
                for error in address.errors:
                    response['errors'].append(error)
        else:
            request.db_session.rollback()
            response = json_response_content('error', 'Some error occured during user creation')
            request.db_session.rollback()
            for error in user.errors:
                response['errors'].append(error)
        return JsonResponse(response)
    company_names = request.db_session.query(Company).all()
    return render_to_response('profile_add.html',
                              {'operation': 'add', 'company_names': company_names, 'timezones': pytz.common_timezones},
                              context_instance=RequestContext(request))


@login_required()
@permission_required('user_edit_own_profile')
def edit(request):
    if request.POST:
        p = request.POST
        user = request.user
        user.first_name = p.get('i_first_name', '')
        user.last_name = p.get('i_last_name', '')
        user.phone = phone_number_from_request(request.POST, 'i_phone')
        user.m_phone = phone_number_from_request(request.POST, 'i_m_phone')
        user.user_type = request.user.user_type
        user.company = request.user.company
        address = address_from_request(request.POST, user.address)
        user.address = address
        if user.no_errors() and address.no_errors():
            request.db_session.add_all([user, address])
            request.db_session.commit()
            response = json_response_content('success', 'Worker was updated successfully')
            response['redirect_url'] = reverse('profiles.views.view')
            # return HttpResponseRedirect(reverse('profiles.views.view'))
        else:
            response = json_response_content('error', 'Some error occured during user creation')
            for error in user.errors:
                response['errors'].append(error)
            for error in address.errors:
                response['errors'].append(error)
        return JsonResponse(response)
    return render_to_response('profile_add.html',
                              {'operation': 'edit',
                               'person': request.user},
                              context_instance=RequestContext(request))


@login_required
@permission_required('user_edit')
def edit_by_id(request, user_id):
    try:
        user = request.db_session.query(User).filter_by(id=user_id).one()
    except:
        raise Http404
    if request.POST:
        user.first_name = request.POST.get('i_first_name', '')
        user.last_name = request.POST.get('i_last_name', '')
        user.phone = phone_number_from_request(request.POST, 'i_phone')
        user.m_phone = phone_number_from_request(request.POST, 'i_m_phone')
        user.company = request.user.company
        address = address_from_request_for_profile(request.POST, user.address)
        user.address = address
        if user.no_errors() and address.no_errors():
            request.db_session.commit()
            # return HttpResponseRedirect(reverse('profiles.views.view'))
            response = json_response_content('success', 'Worker was updated successfully')
            response['redirect_url'] = reverse('profiles.views.view')
        else:
            response = json_response_content('error', 'Some error occured during user creation')
            for error in user.errors:
                response['errors'].append(error)
            for error in address.errors:
                response['errors'].append(error)
        return JsonResponse(response)
    return render_to_response('profile_add.html',
                              {'operation': 'edit',
                               'person': user},
                              context_instance=RequestContext(request))


@login_required
@permission_required('user_set_perms')
def perms_by_id(request, user_id):
    prefix = "perm_"
    errors = []
    sys_objects = request.db_session.query(SysObject).all()
    try:
        user = request.db_session.query(User).filter_by(id=user_id).one()
    except:
        raise Http404
    if user.is_su:
        raise PermissionDenied
    if request.POST:
        print request.POST
        user_groups = []
        for group_id in request.POST.getlist('user_groups'):
            try:
                group = request.db_session.query(
                    Group).filter_by(id=int(group_id)).one()
                if group in request.user.company.user_groups:
                    user_groups.append(group)
                else:
                    errors.append({'field': 'Groups',
                                   'message': 'Group with id %s does not belong this company.' % group_id})
            except NoResultFound:
                errors.append({'field': 'Groups',
                               'message': 'No group with id %s.' % group_id})
        functions = []
        for function in request.db_session.query(SysFunction).all():
            if prefix + str(function.id) in request.POST:
                functions.append(function)
        if not errors:
            user.groups = user_groups
            user.permissions = functions
            request.db_session.commit()
            return HttpResponseRedirect(reverse('companies.views.staff_list'))
    return render_to_response('profile_perms.html',
                              {'errors': errors,
                               'person': user,
                               'sys_objects': sys_objects,
                               'prefix': prefix,
                               },
                              context_instance=RequestContext(request))


# @login_required()
# @require_POST
# def ajax_save_profile(request, form_name):
#     user = request.user
#     p = request.POST
#     if form_name == 'basic_info':
#         user.first_name = p.get('s-f-name', '')
#         user.last_name = p.get('s-l-name', '')
#     elif form_name == 'address':
#         if not user.address:
#             user.address = Address()
#         user.address.line_1 = p.get('s-a-address1', '')
#         user.address.line_2 = p.get('s-a-address2', '')
#         user.address.city = p.get('s-a-city', '')
#         user.address.postalcode = p.get('s-a-code', '')
#         user.address.state = p.get('s-a-state', '')
#         user.address.country = p.get('s-a-country', '')
#     elif form_name == 'contact_info':
#         try:
#             user.phone = pn.format_number(pn.parse(p.get('s-c-phone', ''), "US"), pn.PhoneNumberFormat.E164)
#         except pn.NumberParseException:
#             user.phone = ""
#         try:
#             user.m_phone = pn.format_number(pn.parse(p.get('s-c-mobile', ''), "US"), pn.PhoneNumberFormat.E164)
#         except pn.NumberParseException:
#             user.m_phone = ""
#         user.email2 = p.get('s-c-email', '')
#     request.db_session.commit()
#
#     return HttpResponse(json.dumps(p), content_type="application/json")
