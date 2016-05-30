# -*- coding: utf-8 -*-
from django.core import mail
from django.http import Http404, HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.conf import settings as p_settings

from sqlalchemy.orm.query import Query
from sqlalchemy import and_, or_

from Model import Company, User, Group, CompanyPaymentSystem, Language, CompanySkipDates, CompanySkipWeekdays
from Model import Timezone, Currency, NoInternetOperation, PreauthMethod, CompanySettings, TariffPlan, Deal, DealType
from Model import CompanyKioskManager, CompanySite, VideoFile, VideoSchedule, CompanySocialCommunity
from Model import SocialCommunityBrand, UserRestorePassword, SysObject, SysFunction, GroupPermission

from WebApp.utils import save_file, random_string, alchemy_to_json
from acc.decorators import permission_required
from acc.shortcuts import address_from_request, phone_number_from_request
from acc.utils import process_archive
from libs.validators.core import json_response_content, validation_error
from libs.utils.json_functions import convert_json_keys_to_camelcase

from json import loads
from urlparse import urlparse

import json
import os
import uuid
import hashlib

__author__ = 'D.Ivanets, D.Kalpakchi'


# Check the company id and permission
def check_company_id(request, company_id):
    company = request.db_session.query(Company).filter_by(id=company_id).first() if company_id else ''
    is_f, is_c = request.user.is_focus, request.user.is_company
    if company and (is_f or is_c):
        if not ((is_c and company.id == request.user.company.id) or is_f):
            raise PermissionDenied
    else:
        raise Http404
    return {'company': company, 'is_f': is_f, 'is_c': is_c}


def check_img(image_file):
    from PIL import Image
    try:
        img = Image.open(image_file)
        size = img.size
        width, height = size[0], size[1]
        if width >= 300:
            return 'Width more than 300 pixels.'
        elif height >= 300:
            return 'Height more than 300 pixels.'
    except:
        # Not Image
        return 'The file is not an image.'
    return ''


def save_company_sites(request, info, company):
    response = json_response_content('success', 'Your domain is successfully binded')
    site = company.site if company.site else CompanySite(company.id)
    request.db_session.add(site)
    parsedUrl = urlparse(info.get('domain').lower())
    domain = parsedUrl.netloc or parsedUrl.path or None
    logo = request.FILES.get('logo', None)
    if logo:
        check_msg = check_img(logo)
        if check_msg:
            site.errors.append({'field': 'logo', 'message': check_msg})
    site.domain = domain
    site.support_email = info.get('supportEmail', None)
    if site.no_errors():
        request.db_session.commit()
        if logo and logo.content_type.split('/')[0] == 'image':
            new_name = uuid.uuid1().hex
            extension = logo.name.split('.')[-1]
            logo_path = '%s.%s' % (new_name, extension)
            path = 'company/%d/sites/logos/%s' % (company.id, logo_path)
            save_file(logo, path)
            company.site.logo_path = logo_path
    else:
        request.db_session.rollback()
        response = json_response_content('error', 'Something went wrong during domain changing')
        for error in site.errors:
            response['errors'].append(error)
    return response


@permission_required('company_add')
def add(request):
    if request.method == 'POST':
        data = loads(request.POST.get('data'))
        email = data.get('f_admin_email', '')
        password = data.get('f_admin_pass', random_string(8))
        company_name = data.get('f_company_name', '')
        company_email = data.get('f_c_email', '')
        company_card = data.get('f_c_card', '').replace(' ', '')
        company_card_exp = data.get('ccExpiry', '')
        try:
            geolocation = map(float, data.get('geolocation', None).split("|"))
        except:
            geolocation = None
        user = User(email, password)
        company = Company(company_name)
        if request.db_session.query(User).filter_by(email=email).first():
            user.errors.append(
                {'field': 'f_admin_email', 'message': 'User with such email already exists.'})

        if request.db_session.query(Company).filter_by(name=company_name).first():
            company.errors.append(
                {'field': 'f_company_name', 'message': 'Company with such name already exists.'})
            
        user.user_type_id = 2
        user.is_su = True
        user.groups.append(
            request.db_session.query(Group).filter_by(id=2).one())

        company.address = address_from_request(data)
        company.phone = phone_number_from_request(
            data, 'f_c_phone')
        company.alt_phone = phone_number_from_request(
            data, 'f_c_alt_phone')
        company.email = company_email
        company.web_site = data.get('f_c_web', '')
        company.card = company_card
        company.cc_expiry = company_card_exp
        #company.site = CompanySite()
        # company.company_settings.company_payment_system = 
        if geolocation:
            company.address.latitude, company.address.longitude = geolocation
            request.db_session.add(company.address)
        if 'f_company_logo' in request.FILES:
            logo = request.FILES['f_company_logo']
            img_path = '%s.%s' % (uuid.uuid4(), logo.name.split('.')[-1])
            path = 'company_logo/%s' % img_path
            save_file(logo, path)
            company.logo_path = path

        if user.no_errors() and company.no_errors():
            user.company = company
            request.db_session.add_all([user, company])
            request.db_session.commit()
            mail.send_mail('Account registration',
                           'Welcome to [site] \n'
                           'Your registration information: \n'
                           'Email: %s\n'
                           'Password: %s\n' % (email, password),
                           p_settings.DEFAULT_FROM_EMAIL,
                           [email],
                           fail_silently=False)
            response = json_response_content('success', 'Company was successfully registered')
            response['redirect_url'] = reverse('companies.views.view_by_id', args=(company.id,))
        else:
            if user in request.db_session:
                request.db_session.expunge(user)
            if company in request.db_session:
                request.db_session.expunge(company)

            user_errors = list()
            for error in user.errors:
                if error['field'] == 'password':
                    error['field'] = 'f_admin_pass'
                if error['field'] == 'email':
                    error['field'] = 'f_admin_email'
                user_errors.append(error)

            company_errors = list()
            for error in company.errors:
                if error['field'] == 'name':
                    error['field'] = 'f_company_name'
                if error['field'] == 'email':
                    error['field'] = 'f_c_email'
                company_errors.append(error)

            response = json_response_content('error', 'There are errors during new company registration! Please, fix them and try to save again!')
            response['errors'] = user_errors + company_errors
        return JsonResponse(response)
    return render_to_response('company_add.html', {'operation': 'add'},
                              context_instance=RequestContext(request))


@permission_required('company_edit_own')
def edit(request):
    company = request.user.company
    if request.method == 'POST':
        data = loads(request.POST.get('data'))
        company_name = data.get('f_company_name', '')
        company_email = data.get('f_c_email', '')
        f_company_logo = request.FILES.get('f_company_logo', None)

        check_msg = check_img(f_company_logo)
        if check_msg:
            company.errors.append({'field': 'f_company_logo', 'message': check_msg})

        try:
            geolocation = map(float, data.get('geolocation', None).split("|"))
        except:
            geolocation = None
        if request.db_session.query(Company).filter_by(name=company_name).filter(Company.id != company.id).first():
            company.errors.append(
                {'field': 'f_company_name', 'message': 'Company with such name already exists.'})
        company.name = company_name
        company.address = address_from_request(
            data, company.address)
        company.phone = phone_number_from_request(
            data, 'f_c_phone')
        company.alt_phone = phone_number_from_request(
            data, 'f_c_alt_phone')
        company.email = company_email
        company.web_site = data.get('f_c_web', '')
        company.card = data.get('f_c_card', '').replace(' ', '')
        company.cc_expiry = data.get('ccExpiry', '')
        if f_company_logo:
            extension = f_company_logo.name.split('.')[-1]
            img_path = '%s.%s' % (uuid.uuid4(), extension)
            path = 'company_logo/%s' % img_path
            save_file(f_company_logo, path)
            company.logo_path = path
        if geolocation:
            company.address.latitude, company.address.longitude = geolocation
            request.db_session.add(company.address)
        if company.no_errors() and company.address.no_errors():
            request.db_session.add(company)
            request.db_session.commit()
            response = json_response_content('success', 'Company was updated successfully')
            response['redirect_url'] = reverse('companies.views.view')
        else:
            if company in request.db_session:
                request.db_session.expunge(company)
            response = json_response_content('error', 'There are errors during company edit! Please, fix them and try to save again!')

            for error in company.errors:
                if error['field'] == 'name':
                    error['field'] = 'f_company_name'
                response['errors'].append(error)
            for error in company.address.errors:
                response['errors'].append(error)
        return JsonResponse(response)

    return render_to_response('company_add.html', {'operation': 'edit', 'company': company},
                              context_instance=RequestContext(request))


@permission_required('company_edit_any')
def edit_by_id(request, company_id):
    try:
        company = request.db_session.query(Company).filter_by(id=company_id).one()
    except:
        raise Http404
    if request.method == 'POST':
        data = loads(request.POST.get('data'))
        company_name = data.get('f_company_name', '')
        company_email = data.get('f_c_email', '')
        if request.db_session.query(Company).filter_by(name=company_name)\
            .filter(Company.id != company.id).first():
            company.errors.append(
                {'field': 'Company name', 'message': 'Company with such name already exists.'})
        company.name = company_name
        company.address = address_from_request(
            data, company.address)
        company.phone = phone_number_from_request(
            data, 'f_c_phone')
        company.alt_phone = phone_number_from_request(
            data, 'f_c_alt_phone')
        company.email = company_email
        company.web_site = data.get('f_c_web', '')
        company.card = data.get('f_c_card', '').replace(' ', '')
        company.cc_expiry = data.get('ccExpiry', '')
        if 'f_company_logo' in request.FILES:
            logo = request.FILES['f_company_logo']
            img_path = '%s.%s' % (uuid.uuid4(), logo.name.split('.')[-1])
            path = 'company_logo/%s' % img_path
            save_file(logo, path)
            company.logo_path = path

        if company.no_errors():
            request.db_session.add(company)
            request.db_session.commit()
            response = json_response_content('success', 'Company was updated successfully')
            response['redirect_url'] = reverse('companies.views.view_by_id', args=(company_id,))
        else:
            if company in request.db_session:
                request.db_session.expunge(company)
            response = json_response_content('error', 'Some errors occured during editing company')
            response['errors'] = [error for error in company.errors]
        return JsonResponse(response)
    return render_to_response('company_add.html', {'operation': 'edit', 'company': company},
                              context_instance=RequestContext(request))


@permission_required('company_view_any')
def view_list(request):
    companies = request.db_session.query(Company).all()
    return render_to_response('company_list.html', {'companies': companies},
                              context_instance=RequestContext(request))


@permission_required('company_view_own')
def view(request):
    return render_to_response('company_view.html', {'company': request.user.company},
                              context_instance=RequestContext(request))


@permission_required('company_view_any')
def view_by_id(request, company_id):
    try:
        company = request.db_session.query(
            Company).filter_by(id=company_id).one()
    except:
        raise Http404
    return render_to_response('company_view.html', {'company': company},
                              context_instance=RequestContext(request))


@permission_required('user_view')
def staff_list(request):
    try:
        if request.user.is_focus:
            company = ''
            staff = request.db_session.query(User).all()
        elif request.user.is_company:
            company = request.user.company
            staff = request.db_session.query(User).filter_by(
            company=company).filter_by(user_type_id=request.user.user_type_id).all()
        else:
            raise Http404

        return render_to_response('company_staff.html', {'company': company, 'staff': staff},
                                  context_instance=RequestContext(request))
    except:
        raise Http404

@permission_required('user_view')
def staff_list_focus(request):
    try:
        staff = request.db_session.query(User).filter_by(user_type_id=request.user.user_type_id).all()
        return render_to_response('company_staff_focus.html', {'company': '', 'staff': staff},
                                  context_instance=RequestContext(request))
    except:
        raise Http404


@permission_required('user_view')
def user_management(request):
    try:
        query = request.db_session.query(User).filter_by(user_type_id=1)
        if request.user.is_focus:
            company = ''
        elif request.user.is_company:
            company = request.user.company
            query = query.filter_by(company_id=request.user.company.id)
        else:
            raise Http404
        staff = query.all()

        return render_to_response('company_user_management.html', {'company': company, 'staff': staff},
                                  context_instance=RequestContext(request))
    except:
        raise Http404


@permission_required('user_view')
def user_info_by_id(request, user_id):
    user = request.db_session.query(User).filter_by(id=user_id).filter_by(user_type_id=1).first()
    if not user:
        raise Http404
    if request.user.is_company:
        if user.company.id != request.user.company.id:
            raise PermissionDenied

    query = request.db_session.query(Deal).filter_by(user=user).filter(DealType.id != 3).order_by(Deal.dt_start.desc())
    if request.user.is_company:
        query = query.filter_by(company = request.user.company)
    deals = query.all()

    return render_to_response('company_user_info.html', {'person': user, 'deals': deals},
                              context_instance=RequestContext(request))


@require_POST
def send_mail_for_password_restore(request):
    user_id = request.POST.get('user_id', '')
    if user_id:
        user = request.db_session.query(User).filter_by(id=user_id).filter_by(user_type_id=1).first()
        if user:
            if user.company.web_site.startswith("http://"):
                site = user.company.web_site
            else:
                site = "http://" + user.company.web_site
            urp = UserRestorePassword(user)
            text = """Press this link and follow commands to restore your password: \n %s
            If you can't follow the link, then just enter your code: %s
            to the following link: %s
            """ % ('%s%s' % (site,
                            reverse('sites.views.password_restore_confirm',
                                    args=(urp.change_pass_code,),
                                    urlconf='sites.urls')),
                            urp.change_pass_code,
                            '%s%s' % (site, reverse('sites.views.password_restore_default',
                                                                            args=(),
                                                                            urlconf='sites.urls')))
            mail.send_mail('Password restoring.',
                           text,
                           settings.DEFAULT_FROM_EMAIL,
                           [user.email],
                           fail_silently=False)
            request.db_session.add(urp)
            response = json_response_content('success', 'Email with link to password restore was successfully sent.')
            request.db_session.commit()
        else:
            response = json_response_content('error', "No such user")
    else:
        response = json_response_content('error', "No user id in request")
    return JsonResponse(response)


@permission_required('user_view, company_view_any')
def staff_list_by_id(request, company_id):
    try:
        company = request.db_session.query(
            Company).filter_by(id=int(company_id)).one()
        staff = request.db_session.query(User).filter_by(
            company=company).filter_by(user_type_id=2).all()
        return render_to_response('company_staff.html', {'company': company, 'staff': staff},
                                  context_instance=RequestContext(request))
    except:
        raise Http404

@login_required
@permission_required('company_view_settings')
def company_settings(request, company_id):
    r = check_company_id(request, company_id)
    company = r['company']
    #company = request.db_session.query(Company).filter_by(id=int(company_id)).first()
    company_settings = company.company_settings
    if not company_settings:
        company_settings = CompanySettings(company)
        request.db_session.add(company_settings)
        request.db_session.commit()
        response = json_response_content('warning', 'This company has no settings')
    if request.user.is_focus:
        tariff_plans = company.tariff_plans
        payment_systems = company.payment_systems
        languages = company.company_settings.languages
    else:
        tariff_plans = request.user.company.tariff_plans
        payment_systems = request.user.company.payment_systems
        languages = request.user.company.company_settings.languages
    response = json_response_content('success', 'Your company settings were loaded successfully')
    response['data'].update(convert_json_keys_to_camelcase(alchemy_to_json(company_settings)))
    response['data'].update({
        'company': company,
        'tDayStart': company_settings.t_day_start,
        'tReturn': company_settings.t_return,
        'skipWeekdays': [int(day.weekday) for day in company_settings.skip_weekdays],
        'skipDates': company_settings.skip_dates,
        'timezones': request.db_session.query(Timezone).all(),
        'currencies': request.db_session.query(Currency).all(),
        'preauth_methods': request.db_session.query(PreauthMethod).all(),
        'no_internet_operations': request.db_session.query(NoInternetOperation).all(),
        'tariff_plans': tariff_plans,
        'payment_systems': payment_systems,
        'allLanguages': request.db_session.query(Language).all(),
        'companyLanguageId': [lang.id for lang in languages]
    })
    return render_to_response('company_settings.html', response, context_instance=RequestContext(request))

@login_required
@permission_required('company_view_settings')
def settings_list(request):
    if request.user.is_focus:
        companies = request.db_session.query(Company).all()
        return render_to_response('company_settings_list.html', {'companies': companies}, context_instance=RequestContext(request))


@login_required
@permission_required('company_view_settings')
def settings(request):
    def update_fields(obj, post_fields):
        obj.speaker_volume = post_fields['speakerVolume']
        obj.rent_tax_rate = post_fields['rentTaxRate'].replace(',', '.')
        obj.sale_tax_rate = post_fields['saleTaxRate'].replace(',', '.')
        obj.tax_jurisdiction = post_fields['taxJurisdiction']
        obj.reservation_expiration_period = post_fields['reservationExpirationPeriod']
        obj.max_disks_per_card = post_fields['maxDisksPerCard']
        obj.grace_period = post_fields['gracePeriod']
        obj.sale_convert_type = post_fields['saleConvertType']
        obj.sale_convert_days = post_fields['saleConvertDays']
        obj.sale_convert_price = post_fields['saleConvertPrice'].replace(',', '.')
        obj.capture_retry_interval = post_fields['captureRetryInterval']
        obj.capture_retry_quantity = post_fields['captureRetryQuantity']
        try:
            obj.contact_telephone_number = phone_number_from_request(post_fields, 'contactTelephoneNumber')
        except Exception, e:
            obj.errors.append({'field': 'contactTelephoneNumber', 'message': e.message})
        obj.terms = post_fields['terms']
        obj.is_bluray_warning = post_fields['isBluRayWarning']
        obj.is_smart_capture_retry = post_fields['isSmartCaptureRetry']
        obj.empty_slots_warning = post_fields['emptySlotsWarning']

    def update_relations(obj, post_fields):
        request.db_session.autoflush = False  # Now this is for stub - check out flush
        # This pretends to be the specific validation - that's why this is not in model
        def query_field(name, field_name, selector, default=-1):
            try:
                return getattr(Query, selector)(request.db_session.query(name)
                                                .filter_by(id=int(post_fields.get(field_name, default))))
            except ValueError:
                obj.errors.append({
                    'field': field_name,
                    'message': 'Given value is empty. Please check it out.'
                })

        obj.timezone = query_field(Timezone, 'timezone', 'one', 1)
        obj.t_day_start = fields.get('tDayStart', '')
        obj.t_return = fields.get('tReturn', '')
        obj.currency = query_field(Currency, 'currency', 'one', 109)
        obj.dvd_tariff_plan = query_field(TariffPlan, 'dvdTariffPlan', 'first')
        obj.blu_ray_tariff_plan = query_field(TariffPlan, 'bluRayTariffPlan', 'first')
        obj.game_tariff_plan = query_field(TariffPlan, 'gameTariffPlan', 'first')
        obj.company_payment_system = query_field(CompanyPaymentSystem, 'paymentSystem', 'first')
        obj.dvd_preauth_method = query_field(PreauthMethod, 'dvdPreauthMethod', 'one')
        if obj.dvd_preauth_method.alias == 'customamount':
            obj.dvd_preauth_amount = fields['dvdPreauthAmount'].replace(',', '.')
        else:
            obj.dvd_preauth_amount = None
        obj.blu_ray_preauth_method = query_field(PreauthMethod, 'bluRayPreauthMethod', 'one')
        if obj.blu_ray_preauth_method.alias == 'customamount':
            obj.blu_ray_preauth_amount = fields['bluRayPreauthAmount'].replace(',', '.')
        else:
            obj.blu_ray_preauth_amount = None
        obj.game_preauth_method = query_field(PreauthMethod, 'gamePreauthMethod', 'one')
        if obj.game_preauth_method.alias == 'customamount':
            obj.game_preauth_amount = fields['gamePreauthAmount'].replace(',', '.')
        else:
            obj.game_preauth_amount = None
        obj.rent_no_internet_op = query_field(NoInternetOperation, 'rentNoInternetOpId', 'one')
        obj.sale_no_internet_op = query_field(NoInternetOperation, 'saleNoInternetOpId', 'one')

        langs = request.db_session.query(Language) \
            .filter(Language.id.in_([int(i) for i in post_fields['languageButtons']])).all()
        if len(langs) > 0:
            obj.languages = langs
        else:
            obj.errors.append({
                'field': 'languageButtons',
                'message': 'Choose at least one language, please.'
            })

        request.db_session.query(CompanySkipWeekdays).filter_by(company_settings_id = obj.id).delete()
        for skipped in map(int, post_fields.get('skipWeekdays', [])):
            day = CompanySkipWeekdays(obj, skipped)
            obj.skip_weekdays.append(day)
            request.db_session.add(day)
        
        if post_fields.get('day', False) and post_fields.get('month', False) and post_fields.get('year', False):
            days = map(int, post_fields['day'] if isinstance(post_fields['day'], list) else [post_fields['day']])
            months = map(int, post_fields['month'] if isinstance(post_fields['month'], list) else [post_fields['month']])
            years = map(int, post_fields['year'] if isinstance(post_fields['year'], list) else [post_fields['year']])

            already_skipped_dates = map(lambda x: (int(x.day), int(x.month), int(x.year)), obj.skip_dates)
            for skipped in zip(days, months, years):
                yearly_skipped = (skipped[0], skipped[1], 0)
                if skipped not in already_skipped_dates and yearly_skipped not in already_skipped_dates:
                    date = CompanySkipDates(obj, skipped)
                    obj.skip_dates.append(date)
                    already_skipped_dates.append(skipped)
                    request.db_session.add(date)

        request.db_session.autoflush = True

    if request.user.is_focus:
        data = loads(request.POST.get('data'))
        company_id = int(data['settings']['company_id'])
        company = request.db_session.query(Company).filter_by(id=company_id).first()
        company_settings = company.company_settings
    else:
        company_settings = request.user.company.company_settings
    if not company_settings:
        if request.user.is_focus:
            company_settings = CompanySettings(company)
        else:
            company_settings = CompanySettings(request.user.company)
        request.db_session.add(company_settings)
        request.db_session.commit()
        response = json_response_content('warning', 'This company has no settings')

    if request.method == 'POST':
        if 'company_edit_settings' not in request.user.rights:
            raise PermissionDenied
        if 'response' in locals():
            company_settings = CompanySettings()
        data = loads(request.POST.get('data'))
        fields = data['settings']
        update_fields(company_settings, fields)
        update_relations(company_settings, fields)
        if company_settings.no_errors():
            marked = loads(request.POST.get('markedSkipDates'))
            if marked:
                try:
                    from sqlalchemy.sql.expression import false
                    skip_dates = request.db_session.query(CompanySkipDates)
                    filter_marked = false()
                    for skip_date in marked:
                        filter_marked = filter_marked | (and_(
                            CompanySkipDates.day == skip_date['day'], 
                            CompanySkipDates.month == skip_date['month'],
                            CompanySkipDates.year == skip_date['year']
                        ))
                    skip_dates.filter(filter_marked).filter_by(company_settings_id=marked[0]['id']).delete()
                except Exception, e:
                    return JsonResponse(json_response_content('error',
                        'Some errors occured during deleting skipped dates. Nothing changed.'))
            response = json_response_content('success', 'Company settings updated successfully')
            response['data'] = convert_json_keys_to_camelcase(alchemy_to_json(company_settings))
            request.db_session.add(company_settings)
            request.db_session.commit()
        else:
            if company_settings in request.db_session:
                request.db_session.expunge_all()
            response = json_response_content('error', 'Some errors occurred during company settings update')
            for error in company_settings.errors:
                response['errors'].append(error)
        return JsonResponse(response, safe=False)
    elif request.method == "GET":
        if not 'response' in locals():
            response = json_response_content('success', 'Your company settings were loaded successfully')
            response['data'].update(convert_json_keys_to_camelcase(alchemy_to_json(company_settings)))
        response['data'].update({
            'tDayStart': company_settings.t_day_start,
            'tReturn': company_settings.t_return,
            'skipWeekdays': [int(day.weekday) for day in company_settings.skip_weekdays],
            'skipDates': company_settings.skip_dates,
            'timezones': request.db_session.query(Timezone).all(),
            'currencies': request.db_session.query(Currency).all(),
            'preauth_methods': request.db_session.query(PreauthMethod).all(),
            'no_internet_operations': request.db_session.query(NoInternetOperation).all(),
            'tariff_plans': request.user.company.tariff_plans,
            'payment_systems': request.user.company.payment_systems,
            'allLanguages': request.db_session.query(Language).all(),
            'companyLanguageId': [lang.id for lang in request.user.company.company_settings.languages]
        })
        return render_to_response('company_settings.html', response, context_instance=RequestContext(request))

# @login_required()
# @require_POST
# def ajax_change_logo(request):
# """
#
#     :param request:
#     :return:
#     """
#     if 'upload_logo' in request.FILES:
#         data = request.FILES['upload_logo']
#         img_path = '%s.%s' % (uuid.uuid4(), data.name.split('.')[-1])
#         path = 'company_logo/%s' % img_path
#         save_file(data, path)
#         company = request.db_session.query(Company).filter_by(id=int(request.POST.get('company_id', 0))).one()
#         company.logo_path = path
#         return HttpResponse(json.dumps({'error': False, 'src': path}),
#                             content_type="application/json")
#
#
# @login_required()
# @require_POST
# def ajax_add_company(request):
#     p = request.POST
#     message = ''
#     c_id = p.get('f_company_id', '')
#     email = p.get('f_admin_email', '')
#     if c_id:
#         company = request.db_session.query(Company).filter_by(id=c_id).first()
#         company.name = p.get('f_company_name', '')
#     elif not email_valid(email):
#         return HttpResponse(json.dumps({'error': True, 'message': "Invalid Email address"}),
#                             content_type="application/json")
#     else:
#         company = Company(p.get('f_company_name', ''))
#         password = p.get('f_admin_pass', random_string(8))
#         user = User(email, password)
#         user.user_type_id = 2
#         user.company = company
#         request.db_session.add_all([user, company])
#         mail.send_mail('Account registration',
#                        'Welcome to [site] \n'
#                        'Your registration information: \n'
#                        'Email: %s\n'
#                        'Password: %s\n' % (email, password),
#                        'admin@localhost',
#                        [email],
#                        fail_silently=False)
#     address = company.address
#     if not address:
#         address = Address()
#         company.address = address
#         request.db_session.add(address)
#     address.line_1 = p.get('i_addr1', '')
#     address.line_2 = p.get('i_addr2', '')
#     address.city = p.get('i_city', '')
#     address.state = p.get('i_state', '')
#     address.postalcode = p.get('i_post', '')
#     address.country = p.get('i_country', '')
#     try:
#         company.phone = pn.format_number(pn.parse(p.get('f_c_phone', ''), "US"), pn.PhoneNumberFormat.E164)
#     except pn.NumberParseException:
#         company.phone = ""
#     try:
#         company.alt_phone = pn.format_number(pn.parse(p.get('f_c_alt_phone', ''), "US"), pn.PhoneNumberFormat.E164)
#     except pn.NumberParseException:
#         company.alt_phone = ""
#     company.email = p.get('f_c_email', '')
#     company.web_site = p.get('f_c_web', '')
#     company.card = p.get('f_c_card', '').replace(' ', '')
#     if 'f_company_logo' in request.FILES:
#         data = request.FILES['upload_logo']
#         img_path = '%s.%s' % (uuid.uuid4(), data.name.split('.')[-1])
#         path = 'company_logo/%s' % img_path
#         save_file(data, path)
#         company.logo_path = path
#     request.db_session.commit()
#
#     return HttpResponse(json.dumps({'error': message and True or False,
#                                     'message': message,
#                                     'user': request.user.user_type.name}),
#                         content_type="application/json")

# @login_required()
# @require_POST


def upload(request):
    return render_to_response('upload_archive.html', context_instance=RequestContext(request))


def ajax_upload_archive(request):
    """
    :param request:
    :return:
    """
    if 'key_archive' in request.FILES:
        pay_id, username, password = process_archive(
            request.FILES['key_archive'])
        # We have to process this result in some way
        return HttpResponse(json.dumps({'error': False, 'username': username, 'password': password}),
                            content_type="application/json")
    return HttpResponse(json.dumps({'error': True, 'src': None}),
                        content_type="application/json")


@login_required
@permission_required('company_view_permissions')
def permissions(request, company_id=None):
    if request.method == "GET":
        if company_id:
            company = request.db_session.query(Company).filter_by(id=company_id).first()
        else:
            company = request.user.company
        granted_users = request.db_session.query(CompanyKioskManager).filter_by(company_id=company.id).all()
        company_granted = [ckm.user for ckm in granted_users]
        return render(request, 'company_permissions.html', 
            { 'users': [u for u in company.users if u not in company_granted], 'granted': granted_users,
            'companyId': company.id, 'viewingOwnCompany': company_id is None})
    else:
        raise Http404


@login_required
@require_POST
def add_permission(request, company_id):
    user_id = request.POST.get('userId', None)
    if user_id:
        granted_user = CompanyKioskManager(company_id, user_id)
        request.db_session.add(granted_user)
        request.db_session.commit()
        response = json_response_content('success', 'Permissions granted successfully')
        response['data'] = {
            'granted_full_name': granted_user.user.full_name
        }
        # return JsonResponse(response)
        return HttpResponseRedirect(reverse('companies.views.permissions', args=(company_id,)))
    else:
        return JsonResponse(json_response_content('error', 'User field is required'))


@login_required
def remove_permission(request, company_id, user_id):
    from decimal import Decimal
    granted_user = request.db_session.query(CompanyKioskManager).\
        filter_by(company_id=company_id, user_id=user_id).first()
    request.db_session.delete(granted_user)
    request.db_session.commit()
    response = json_response_content('success', 'Company permission removed successfully')
    response['redirect_url'] = reverse('companies.views.permissions', args=(Decimal(company_id),))
    return JsonResponse(response)


@login_required
@permission_required('company_view_sites')
def company_sites(request, company_id=None):
    r = check_company_id(request, company_id)
    company = r['company']
    return render(request, 'company_sites.html', {'site': company.site, 'company': company})


@login_required
@require_POST
@permission_required('company_edit_sites')
def ajax_save_company_sites(request, company_id=None):
    #print "\n\nStart\n\n"
    r = check_company_id(request, company_id)
    company = r['company']
    #print "-== ajax_save_company_sites ==-"
    info = loads(request.POST.get('site', None))
    #print "info =", info
    if not info:
        raise Http404
    response = save_company_sites(request, info, company)
    return JsonResponse(response)

    company = request.user.company
    if request.method == "POST":
        if 'company_edit_sites' not in request.user.rights:
            raise PermissionDenied
        from urlparse import urlparse
        info = loads(request.POST.get('site', None))
        logo = request.FILES.get('logo', None)
        response = json_response_content('success', 'Your domain is successfully binded')
        if info:
            parsedUrl = urlparse(info.get('domain'))
            domain = parsedUrl.netloc or parsedUrl.path or None
            if domain is not None:
                domain_repeating = request.db_session.query(CompanySite).filter_by(domain=domain).all()
                if not domain_repeating:
                    site = CompanySite(company.id)
                    site.domain = domain
                    request.db_session.merge(site)
                    request.db_session.commit()
                    response['data']['domain'] = domain
                else:
                    response = json_response_content('error', 'Such domain is already registered')
                    response['errors'].append(validation_error('domain', 'Such domain is already registered'))
                    request.db_session.expunge_all()
            support_email = info.get('supportEmail', None)
            try:
                validate_email(support_email)
                company.site.support_email = support_email
            except:
                response['type'] = 'error'
                response['errors'].append(validation_error('supportEmail', 'Such email is invalid'))
                request.db_session.expunge_all()
        logo = request.FILES.get('logo', None)
        if logo:
            if logo.content_type.split('/')[0] == 'image':
                new_name = uuid.uuid1().hex
                extension = logo.name.split('.')[-1]
                logo_path = '%s.%s' % (new_name, extension)
                path = 'company/%d/sites/logos/%s' % (company.id, logo_path)
                save_file(logo, path)
                company.site.logo_path = logo_path
            else:
                response = json_response_content('error', 'Wrong mimetype')
                response['errors'].append(validation_error('logo', 'Given file is not a video file'))
                request.db_session.expunge_all()
        request.db_session.add(company.site)
        return JsonResponse(response)
    elif request.method == "GET":
        if request.user.is_focus:
            site = ''
        else:
            site = company.site
        return render(request, 'company_sites.html', {'site': site})
    else:
        raise Http404


@login_required
@permission_required('company_view_sites')
def sites(request):
    company = request.user.company
    if request.method == "POST":
        if 'company_edit_sites' not in request.user.rights:
            raise PermissionDenied
        info = loads(request.POST.get('site', None))
        if not info:
            raise Http404
        response = save_company_sites(request, info, company)
        return JsonResponse(response)


        # if logo:
        #     if logo.content_type.split('/')[0] == 'image':
        #         new_name = uuid.uuid1().hex
        #         extension = logo.name.split('.')[-1]
        #         logo_path = '%s.%s' % (new_name, extension)
        #         path = 'company/%d/sites/logos/%s' % (company.id, logo_path)
        #         save_file(logo, path)
        #         company.site.logo_path = logo_path
        # #     else:
        # #         response = json_response_content('error', 'Wrong mimetype')
        # #         response['errors'].append(validation_error('logo', 'Given file is not an image file'))
        # #         request.db_session.expunge_all()
        # # request.db_session.add(company.site)
        # # return JsonResponse(response)

    elif request.method == "GET":
        site = company.site if not request.user.is_focus else ''
        return render(request, 'company_sites.html', {'site': site})
    else:
        raise Http404


@login_required
@permission_required('company_view_trailers')
def trailers(request):
    if request.user.is_focus:
        companies = request.db_session.query(Company).all()
    query = request.db_session.query(VideoFile)
    if request.user.is_company:
        companies = []
        query = query.filter_by(company_id=request.user.company.id)
    video_files = query.all()
    #video_files = request.db_session.query(VideoFile).filter_by(company_id=request.user.company.id).all()
    return render(request, 'company_trailers.html', locals())


@login_required
@permission_required('company_add_trailer')
def remove_trailer(request, trailer_id):
    if trailer_id:
        query = request.db_session.query(VideoFile).filter_by(id=int(trailer_id))
        if request.user.is_company:
            query = query.filter_by(company_id=request.user.company.id)
        video_file = query.first()

        if not video_file:
            raise PermissionDenied
        print video_file.alias
        request.db_session.delete(video_file)
        request.db_session.commit()
        return HttpResponseRedirect(reverse('companies.views.trailers'))
    else:
        raise Http404


@login_required()
@require_POST
@permission_required('company_add_trailer')
def ajax_edit_trailer(request):
    mode = request.POST.get('mode')
    if mode == 'edit':
        data = loads(request.POST.get('data', ''))
        trailer_id = data['trailer_id']

        if not trailer_id:
            raise PermissionDenied

        query = request.db_session.query(VideoFile).filter_by(id=int(trailer_id))
        if request.user.is_company:
            query = query.filter_by(company_id=request.user.company.id)
        video_file = query.first()

        video_file.alias = data['title'].lower() if video_file.company else data['title'].upper()
        request.db_session.add(video_file)
        request.db_session.commit()
        response = json_response_content('success', "Trailer was saved successfully")
        return JsonResponse(response)


@login_required
@permission_required('company_add_trailer')
def edit_trailer(request, trailer_id):
    if trailer_id:
        query = request.db_session.query(VideoFile).filter_by(id=int(trailer_id))
        if request.user.is_company:
            query = query.filter_by(company_id=request.user.company.id)
        video_file = query.first()

        if not video_file:
            raise PermissionDenied

        return render_to_response('company_edit_trailers.html', {'video_file': video_file,},
                                  context_instance=RequestContext(request))
    else:
        raise Http404


@login_required
@require_POST
@permission_required('company_add_trailer')
def add_trailer(request):
    video = request.FILES.get('video', None)
    trailer_info = loads(request.POST.get('trailer', None))

    if request.user.is_focus:
        if trailer_info['f_company_id']:
            company_id = int(trailer_info['f_company_id'])
            company = request.db_session.query(Company).filter_by(id=company_id).first()
        else:
            company = None
    else:
        company = request.user.company
    if video:
        if video.content_type.split('/')[0] == 'video':
            new_name = uuid.uuid1().hex
            extension = video.name.split('.')[-1]
            video_path = '%s.%s' % (new_name, extension)
            path = 'video/%d/%s' % (company.id if company else 0, video_path)
            save_file(video, path)

            video_file = VideoFile(company.id if company else None, video_path, trailer_info['title'].lower() if company else trailer_info['title'].upper())
            video_file.hash = hashlib.md5(open(os.path.join(p_settings.MEDIA_ROOT, path), 'rb').read()).hexdigest()
            video_file.length = 0

            request.db_session.add(video_file)
            request.db_session.commit()

            trailer_id = video_file.id
            response = json_response_content('success', "Trailer was added successfully")

            response['data'] = {
                'id': video_file.id,
                'title': video_file.alias,
                'length': video_file.length,
                'dtModify': video_file.dt_modify,
                'trailer_id': trailer_id,
            }

            if request.user.is_focus:
                response['data']['focus'] = True
                response['data']['company'] = company.name if company else 'All Companies'
                response['data']['company_id'] = company.id if company else ''
        else:
            response = json_response_content('error', 'Wrong MIME type!')
            response['errors'].append(validation_error('trailer', 'Given file is not a video file'))
    else:
        response = json_response_content('error', 'No video was given')
        response['errors'].append(validation_error('trailer', 'No video file was given'))
    return JsonResponse(response)


@permission_required('company_view_social')
def social(request):
    if request.method == "POST":
        if 'company_add_social' not in request.user.rights:
            raise PermissionDenied
        info = loads(request.POST.get('community', None))
        logo = request.FILES.get('logo', None)
        company = request.user.company
        if info:
            if request.user.is_focus:
                company_id = int(info['f_company_id'])
                community = CompanySocialCommunity(company_id, info['brand'], info['url'])
            else:
                community = CompanySocialCommunity(request.user.company.id, info['brand'], info['url'])

            community.alias = info['alias']
            if logo:
                if logo.content_type.split('/')[0] == 'image':
                    new_name = uuid.uuid1().hex
                    extension = logo.name.split('.')[-1]
                    logo_path = '%s.%s' % (new_name, extension)

                    if request.user.is_focus:
                        path = 'company/%d/social/logos/%s' % (company_id, logo_path)
                    else:
                        path = 'company/%d/social/logos/%s' % (company.id, logo_path)

                    save_file(logo, path)
                    community.logo_path = logo_path
                else:
                    response = json_response_content('error', 'Wrong mimetype')
                    response['errors'].append(validation_error('logo', 'Given file is not a video file'))
        request.db_session.add(community)
        request.db_session.commit()

        if request.user.is_focus:
            count = request.db_session.query(CompanySocialCommunity).count()
        else:
            count = request.db_session.query(CompanySocialCommunity).filter_by(company_id=company.id).count()

        if 'response' not in locals():
            response = json_response_content('success', 'Social community was successfully added')
        response['data'] = {
            'companyId': company.id,
            'socialId': community.id,
            'id': count,
            'brand': community.brand.alias,
            'url': community.url,
            'title': community.alias,
            'logo': community.logo_path
        }
        if request.user.is_focus:
            response['data']['focus'] = True
            response['data']['company'] = company.name
            response['data']['company_id'] = company_id

        return JsonResponse(response)
    elif request.method == "GET":

        if request.user.is_focus:
            companies = request.db_session.query(Company).all()
            communities = request.db_session.query(CompanySocialCommunity).all()
        else:
            companies = []
            communities = request.db_session.query(CompanySocialCommunity)\
            .filter_by(company_id=request.user.company.id).all()

        social_brands = request.db_session.query(SocialCommunityBrand).all()
        return render(request, 'company_social.html', locals())
    else:
        raise Http404


def social_remove(request, social_id):
    company = request.user.company
    if social_id:

        if request.user.is_focus:
            community = request.db_session.query(CompanySocialCommunity).filter_by(id=social_id).first()
        else:
            community = request.db_session.query(CompanySocialCommunity).filter_by(id=social_id, company_id=company.id).first()

        if not community:
            raise PermissionDenied
        request.db_session.delete(community)
        request.db_session.commit()
        return HttpResponseRedirect(reverse('companies.views.social'))
    else:
        raise Http404


@permission_required('perms_moderate_groups')
def group_list(request):
    if request.user.is_focus:
        company = ''
        companies = request.db_session.query(Company).all()
        groups = request.db_session.query(Group).all()
    else:
        companies = []
        company = request.user.company
        groups = request.db_session.query(Group).filter_by(company=company).all()
    return render_to_response('company_group_list.html',
                              {'groups': groups,
                               'company': company,
                               'companies': companies},
                              context_instance=RequestContext(request))

@login_required
@require_POST
@permission_required('company_edit_group_permission')
def group_add(request):
    mode = request.POST.get('mode')
    if mode == 'add':
        data = loads(request.POST.get('data', ''))
        if request.user.is_focus:
            company_id = int(data['groupNameField']['f_company_id'])
        group_name = data['groupNameField']['group_name']
        if len(group_name) > 0:
            group = Group()
            group.name = group_name
            if request.user.is_focus:
                group.company_id = company_id
            else:
                group.company = request.user.company
            request.db_session.add(group)
            request.db_session.commit()
            response = json_response_content('success', 'Group add successfully')
        else:
            response = json_response_content('error', 'No group name')
    return JsonResponse(response)


@login_required
@permission_required('company_edit_group_permission')
def remove_group(request, group_id):
    company = request.user.company
    if request.user.is_focus:
        group = request.db_session.query(Group).\
        filter_by(id=group_id).first()
    else:
        group = request.db_session.query(Group).\
            filter_by(company=company, id=group_id).first()
    if group:
        request.db_session.delete(group)
        request.db_session.commit()
        response = json_response_content('success', 'Company permission removed successfully')
    else:
        response = json_response_content('error', 'Access denied')
    return JsonResponse(response)


@login_required
@permission_required('company_edit_group_permission')
def edit_group(request, group_id):
    prefix = "perm_"
    company = request.user.company
    if request.user.is_focus:
        group = request.db_session.query(Group).\
            filter_by(id=group_id).first()
    else:
        group = request.db_session.query(Group).\
            filter_by(company_id=company.id, id=group_id).first()
    if group:
        sys_objects = request.db_session.query(SysObject).all()
        functions = []
        for function in request.db_session.query(GroupPermission).filter_by(group_id=group_id).all():
            functions.append(function.function_id)
        #group.permissions = functions
    else:
        raise Http404
    return render_to_response('company_group_edit.html',
                              {'sys_objects': sys_objects,
                               'group': group,
                               'functions': functions,
                               'prefix': prefix,
                               'company': company},
                              context_instance=RequestContext(request))


@login_required
@require_POST
@permission_required('company_edit_group_permission')
def save_group(request, group_id):
    prefix = "perm_"
    company = request.user.company
    if request.user.is_focus:
        group = request.db_session.query(Group).\
            filter_by(id=group_id).first()
    else:
        group = request.db_session.query(Group).\
            filter_by(company_id=company.id, id=group_id).first()
    if group:
        mode = request.POST.get('mode')
        if mode == 'save':
            data = loads(request.POST.get('data', ''))
            group_name = data['groupNameField']['group_name']
            if len(group_name) > 0:
                group.name = group_name
                request.db_session.add(group)

                functions = []
                for function in request.db_session.query(SysFunction).all():
                    if prefix + str(function.id) in data['groupNameField']:
                        functions.append(function)
                group.permissions = functions

                request.db_session.commit()
                response = json_response_content('success', 'Group add successfully')
            else:
                response = json_response_content('error', 'No group name')
    else:
        response = json_response_content('error', 'No group name')
    return JsonResponse(response)
