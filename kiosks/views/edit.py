# -*- coding: utf-8 -*-
from json import loads

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse

from Model import Kiosk, Company, Address, KioskSettings, Timezone, Currency, TariffPlan, Slot
from Model import NoInternetOperation, PreauthMethod, Language, CompanyPaymentSystem
from Model import KioskSkipDates, KioskSkipWeekdays

from libs.validators.core import json_response_content
from libs.utils.json_functions import convert_json_keys_to_camelcase
from WebApp.utils import alchemy_to_json, random_string
from acc.shortcuts import phone_number_from_request
from acc.decorators import permission_required
from sqlalchemy.orm.query import Query
from sqlalchemy import or_, and_


@login_required
@permission_required('kiosk_edit')
def settings(request, kiosk_id):
    def update_fields(obj, fields):
        obj.alias = fields.get('alias', '')
        obj.speaker_volume = fields['speakerVolume'].replace(',', '.')
        obj.rent_tax_rate = fields['rentTaxRate'].replace(',', '.')
        obj.sale_tax_rate = fields['saleTaxRate'].replace(',', '.')
        obj.tax_jurisdiction = fields['taxJurisdiction']
        obj.reservation_expiration_period = fields['reservationExpirationPeriod']
        obj.max_disks_per_card = fields['maxDisksPerCard']
        obj.grace_period = fields['gracePeriod']
        obj.sale_convert_type = fields['saleConvertType']
        obj.sale_convert_days = fields['saleConvertDays']
        obj.sale_convert_price = fields['saleConvertPrice'].replace(',', '.')
        obj.capture_retry_interval = fields['captureRetryInterval']
        obj.capture_retry_quantity = fields['captureRetryQuantity']
        try:
            obj.contact_telephone_number = phone_number_from_request(fields, 'contactTelephoneNumber')
        except Exception, e:
            obj.errors.append({'field': 'contactTelephoneNumber', 'message': e.message})
        obj.terms = fields['terms']
        obj.is_bluray_warning = fields['isBluRayWarning']
        obj.is_smart_capture_retry = fields['isSmartCaptureRetry']
        obj.empty_slots_warning = fields['emptySlotsWarning']
        obj.password = fields['password']

    def update_relations(obj, fields):
        request.db_session.autoflush = False    # Now this is for stub - check out flush

        def query_field(name, field_name, selector, default=None):
            return getattr(Query, selector)(
                request.db_session.query(name)
                .filter_by(id=int(fields.get(field_name, default)))) if fields.get(field_name) else None

        # obj.kiosk = query_field(Kiosk, 'kiosk', 'one')
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
        obj.blu_ray_preauth_method = query_field(PreauthMethod, 'bluRayPreauthMethod', 'one')
        if obj.blu_ray_preauth_method.alias == 'customamount':
            obj.blu_ray_preauth_amount = fields['bluRayPreauthAmount'].replace(',', '.')
        obj.game_preauth_method = query_field(PreauthMethod, 'gamePreauthMethod', 'one')
        if obj.game_preauth_method.alias == 'customamount':
            obj.game_preauth_amount = fields['gamePreauthAmount'].replace(',', '.')
        obj.rent_no_internet_op = query_field(NoInternetOperation, 'rentNoInternetOpId', 'one')
        obj.sale_no_internet_op = query_field(NoInternetOperation, 'saleNoInternetOpId', 'one')

        languages = request.db_session.query(Language)\
            .filter(Language.id.in_([int(i) for i in fields['languageButtons']])).all()
        if len(languages) > 0:
            obj.languages = languages
        else:
            obj.errors.append({
                'field': 'languageButtons',
                'message': 'Choose at least one language, please.'
            })

        for sd in request.db_session.query(KioskSkipWeekdays).filter_by(kiosk_settings_id=obj.id).all():
            sd.is_active = False
        for skipped in map(int, fields.get('skipWeekdays', [])):
            day = request.db_session.query(KioskSkipWeekdays)\
                .filter_by(kiosk_settings_id=obj.id).filter_by(weekday=skipped).first()
            day = day or KioskSkipWeekdays(obj, skipped)
            day.is_active = True
            obj.skip_weekdays.append(day)
            request.db_session.add(day)

        if fields.get('day', False) and fields.get('month', False) and fields.get('year', False):
            days = map(int, fields['day'] if isinstance(fields['day'], list) else [fields['day']])
            months = map(int, fields['month'] if isinstance(fields['month'], list) else [fields['month']])
            years = map(int, fields['year'] if isinstance(fields['year'], list) else [fields['year']])

            already_skipped_dates = map(lambda x: (int(x.day), int(x.month), int(x.year)), obj.kiosk.actual_skip_dates)
            for skipped in zip(days, months, years):
                yearly_skipped = (skipped[0], skipped[1], 0)
                if skipped not in already_skipped_dates and yearly_skipped not in already_skipped_dates:
                    date = request.db_session.query(KioskSkipDates)\
                        .filter_by(kiosk_settings_id=obj.id)\
                        .filter_by(day=skipped[0])\
                        .filter_by(month=skipped[1])\
                        .filter_by(year=skipped[2]).first()
                    date = date or KioskSkipDates(obj, skipped)
                    date.is_active = True
                    already_skipped_dates.append(skipped)
                    request.db_session.add(date)
        request.db_session.autoflush = True

    kiosk_settings = request.db_session.query(KioskSettings).filter_by(id=kiosk_id).first()
    kiosk = kiosk_settings.kiosk

    if request.method == "POST":
        data = loads(request.POST.get('data'))
        checked = data.get('settings')
        # checked = data.get('checked')
        update_fields(kiosk_settings, checked)
        update_relations(kiosk_settings, checked)
        if kiosk_settings is None:
            kiosk_settings = KioskSettings()
        if kiosk_settings.no_errors():
            marked = loads(request.POST.get('markedSkipDates'))
            if marked:
                try:
                    from sqlalchemy.sql.expression import false
                    skip_dates = request.db_session.query(KioskSkipDates)
                    filter_marked = false()
                    for skip_date in marked:
                        filter_marked = filter_marked | (and_(
                            KioskSkipDates.day == skip_date['day'],
                            KioskSkipDates.month == skip_date['month'],
                            KioskSkipDates.year == skip_date['year']
                        ))
                    for sd in skip_dates.filter(filter_marked).filter_by(kiosk_settings_id=marked[0]['id']).all():
                        sd.is_active = False

                except:
                    return JsonResponse(json_response_content('error',
                        'Some errors occured during deleting skipped dates. Nothing changed.'))
            response = json_response_content('success', 'Kiosk settings were updated successfully')
            response['redirect_url'] = reverse('kiosks.views.view_list')
            response['data'] = convert_json_keys_to_camelcase(alchemy_to_json(kiosk_settings))
            request.db_session.add(kiosk_settings)
            request.db_session.commit()
            return JsonResponse(response)
        else:
            if kiosk_settings in request.db_session:
                request.db_session.expunge(kiosk_settings)
            response = json_response_content('error', 'Some errors occured during updating kiosk settings')
            for error in kiosk_settings.errors:
                response['errors'].append(error)
            return JsonResponse(response)
    elif request.method == "GET":
        tz = request.db_session.query(Timezone).all()
        cs = request.db_session.query(Currency).all()
        nop = request.db_session.query(NoInternetOperation).all()
        pm = request.db_session.query(PreauthMethod).all()
        languages = request.db_session.query(Language).all()
        response = json_response_content('success', 'Your kiosk settings were loaded successfully')
        response['data'] = convert_json_keys_to_camelcase(alchemy_to_json(kiosk_settings))
        response['data'].update({
            'tDayStart': kiosk_settings.t_day_start,
            'tReturn': kiosk_settings.t_return,
            'timezones': tz,
            'currencies': cs,
            'preauth_methods': pm,
            'no_internet_operations': nop,
            'tariff_plans': kiosk_settings.kiosk.company.tariff_plans,
            'payment_systems': kiosk_settings.kiosk.company.payment_systems,
            'allLanguages': languages,
            'kioskId': kiosk_id,
            'kioskLanguageId': [lang.id for lang in kiosk_settings.languages],
            'skipDates': kiosk.actual_skip_dates,
            'skipWeekdays': [skipped.weekday for skipped in kiosk.actual_skip_days]
        })
        return render(request, 'kiosk_settings.html', response)


@login_required
@permission_required('kiosk_add')
def add(request):
    if request.user.is_focus:
        companies = request.db_session.query(Company).all()
    elif request.user.is_company:
        companies = [request.user.company]
    else:
        raise Http404
    kiosk = Kiosk()
    return render(request, 'kiosk_add.html', locals())


@login_required()
@permission_required('kiosk_edit')
def edit_by_id(request, kiosk_id):
    kiosk = request.db_session.query(Kiosk).filter_by(id=kiosk_id).first()
    companies = request.db_session.query(Company).all()
    if ((not request.user.is_focus)
            and not (request.user.is_company
                     and kiosk.company.id == request.user.company.id)) or not kiosk:
        raise Http404
    return render(request, 'kiosk_edit.html', locals())


@login_required()
@require_POST
def ajax_add_kiosk(request):
    p = request.POST
    message = ''
    k_id = p.get('f_kiosk_id', '')
    try:
        geolocation = map(float, p.get('geolocation', None).split("|"))
    except:
        geolocation = None

    if k_id:
        kiosk = request.db_session.query(Kiosk).filter_by(id=k_id).first()
    else:
        company = request.db_session.query(Company).filter_by(id=int(p.get('f_company_id', 1))).one()
        kiosk = Kiosk(company)
        # TODO: Dima, please, check this code
        k = True
        activation_code = None
        while k:
            activation_code = random_string(8)
            k = request.db_session.query(Kiosk).filter_by(activation_code=activation_code).first()
        kiosk.activation_code = activation_code

        l = []
        for slot_number in range(101, 170) + range(228, 271) + range(501, 571) + range(601, 671):
            s = Slot(number = slot_number, status_id = 1, is_to_check = False)
            request.db_session.add(s)
            l.append(s)
        #request.db_session.commit()
        kiosk.slots = l
    kiosk.group_number = p.get('group_number')
    request.db_session.add(kiosk)
    address = kiosk.address
    if not address:
        address = Address()
        kiosk.address = address
        request.db_session.add(address)

    address.line_1 = p.get('line1', '')
    address.line_2 = p.get('line2', '')
    address.city = p.get('city', '')
    address.state = p.get('state', '')
    address.postalcode = p.get('postalcode', '')
    address.country = p.get('country', '')
    #request.db_session.commit()
    if geolocation:
        address.latitude, address.longitude = geolocation
    if kiosk.no_errors() and address.no_errors():
        request.db_session.commit()
        return JsonResponse(json_response_content('success', 'Kiosk was successfully changed'))
    else:
        request.db_session.expunge_all()
        response = json_response_content('error', 'Something went wrong during kiosk changing')
        for error in kiosk.errors:
            response['errors'].append(error)
        for error in address.errors:
            response['errors'].append(error)
        return JsonResponse(response)