# -*- coding: utf-8 -*-
from json import loads

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render

from Model import Kiosk, Timezone, Currency
from Model import NoInternetOperation, PreauthMethod, Language
from Model import KioskSkipDates, KioskSkipWeekdays
from Model import VideoFile, VideoSchedule

from libs.validators.core import json_response_content, validation_error
from acc.decorators import permission_required
from sqlalchemy import or_, and_


@login_required
@permission_required('kiosk_view', 'kiosk_multi_settings')
def multi_settings(request):
    company = request.user.company
    company_trailers = request.db_session.query(VideoFile.id, VideoFile.alias)\
        .filter(or_(VideoFile.company_id == company.id, VideoFile.company_id == None)).all()

    if request.method == "POST":
        request.db_session.autoflush = False
        data = loads(request.POST.get('data'))
        fields = data['settings']
        checked = data.get('settings')
        password = checked.get('passwordUser', '')
        error_msg = 'Some errors occurred during updating kiosk settings'

        # Validate, that user password is correct
        if not request.user.is_pass_valid(password):
            response = json_response_content('error', error_msg)
            response['errors'].append(
                {'field': 'passwordUser', 'message': "Incorrect password"})
            return JsonResponse(response)

        # Get kiosks to update list and validate,
        # that at least single kiosk selected
        kiosk_ids = fields.get('kiosks', [])

        if type(kiosk_ids) is not list:
            kiosk_ids = [kiosk_ids]

        kiosks = request.db_session.query(Kiosk)\
            .filter(Kiosk.id.in_([int(kid) for kid in kiosk_ids])).all()

        if not kiosks:
            response = json_response_content('error', error_msg)
            response['errors'].append({'field': 'kiosks', 'message': "Select at leas one kiosk"})
            return JsonResponse(response)

        # We will get POST fields one by one and accept their values to
        # appropriate fields.
        data_to_update = {}
        dit_to_coma = lambda x: x.replace(',', '.')
        fields_to_check = (
            ('timezone', 'timezone_id', None),
            ('tDayStart', 't_day_start', None),
            ('tReturn', 't_return', None),
            ('currency', 'currency_id', None),
            ('speakerVolume', 'speaker_volume', None),
            ('rentTaxRate', 'rent_tax_rate', None),
            ('saleTaxRate', 'sale_tax_rate', None),
            ('taxJurisdiction', 'tax_jurisdiction', None),
            ('dvdTariffPlan', 'dvd_tariff_plan_id', None),
            ('bluRayTariffPlan', 'blu_ray_tariff_plan_id', None),
            ('gameTariffPlan', 'game_tariff_plan_id', None),
            ('paymentSystem', 'company_payment_system_id', None),
            ('reservationExpirationPeriod', 'reservation_expiration_period',
             None),
            ('maxDisksPerCard', 'max_disks_per_card', None),
            ('gracePeriod', 'grace_period', None),
            ('dvdPreauthMethod', 'dvd_preauth_method_id', None),
            ('bluRayPreauthMethod', 'blu_ray_preauth_method_id', None),
            ('gamePreauthMethod', 'game_preauth_method_id', None),
            ('rentNoInternetOpId', 'rent_no_internet_op_id', None),
            ('saleNoInternetOpId', 'sale_no_internet_op_id', None),
            ('dvdPreauthAmount', 'dvd_preauth_amount', dit_to_coma),
            ('bluRayPreauthAmount', 'blu_ray_preauth_amount', dit_to_coma),
            ('gamePreauthAmount', 'game_preauth_amount', dit_to_coma),
            ('captureRetryInterval', 'capture_retry_interval', None),
            ('captureRetryQuantity', 'capture_retry_quantity', None),
            ('terms', 'terms', None),
            ('emptySlotsWarning', 'empty_slots_warning', None),
            ('password', 'password', None),
        )

        # Get field values from POST
        for form_name, field_name, func in fields_to_check:
            value = fields.get(form_name)
            if value != '':
                if func:
                    value = func(value)
                data_to_update.update({field_name: value})

        # Generate skip days list
        if fields.get('day', False) and \
                fields.get('month', False) and \
                fields.get('year', False):
            days = map(int, fields['day'] if isinstance(fields['day'], list) else [fields['day']])
            months = map(int, fields['month'] if isinstance(fields['month'], list) else [fields['month']])
            years = map(int, fields['year'] if isinstance(fields['year'], list) else [fields['year']])
            skip_days = zip(days, months, years)
        else:
            skip_days = []

        # Generate skip weekdays list
        skip_weekdays_id = map(int, fields.get('skipWeekdays', []))

        # Set kiosk schedule
        trailers_dict = {int(v.id): v.alias for v in company_trailers}
        schedule = fields.get('schedule', None)
        schedule_errors = []
        if schedule:
            not_yours = [v for v in schedule if int(v) not in trailers_dict.keys()]
            if not_yours:
                schedule_errors.append(validation_error('schedule',
                    "You don't have trailers with ids %s" % ", ".join(not_yours)))
                schedule = None
            else:
                # schedule = VideoSchedule(kiosk_id, "|".join(schedule))
                schedule = "|".join(schedule)

        # apply required values to eack kiosk settings from list
        for kiosk in kiosks:
            settings = kiosk.settings
            for key, value in data_to_update.items():
                settings.__setattr__(key, value)

            # Check whether there were any single week day. If yes, apply new
            # skip_weekdays settings.
            if skip_weekdays_id:
                for sd in settings.skip_weekdays:
                    sd.is_active = False
                for skipped in skip_weekdays_id:
                    day = settings.skip_weekdays_alt \
                        .filter_by(weekday=skipped).first()
                    day = day or KioskSkipWeekdays(settings, skipped)
                    day.is_active = True
                    settings.skip_weekdays.append(day)

            # Add skip dates if exists
            already_skipped_dates = map(lambda x: (int(x.day), int(x.month), int(x.year)), kiosk.actual_skip_dates)
            for skipped in skip_days:
                yearly_skipped = (skipped[0], skipped[1], 0)
                if skipped not in already_skipped_dates and yearly_skipped not in already_skipped_dates:
                    date = request.db_session.query(KioskSkipDates)\
                        .filter_by(kiosk_settings_id=settings.id)\
                        .filter_by(day=skipped[0])\
                        .filter_by(month=skipped[1])\
                        .filter_by(year=skipped[2]).first()
                    date = date or KioskSkipDates(settings, skipped)
                    date.is_active = True
                    already_skipped_dates.append(skipped)
                    settings.skip_dates.append(date)
                    # request.db_session.add(date)

            # Validate data. If there were any error, expunge changes,
            # return validation error response
            if not kiosk.settings.no_errors() or schedule_errors:
                if kiosk.settings in request.db_session:
                    request.db_session.expunge(settings)
                response = json_response_content('error', error_msg)
                for error in kiosk.settings.errors + schedule_errors:
                    response['errors'].append(error)
                return JsonResponse(response)
            else:
                if schedule:
                    kiosk.video_schedule.append(VideoSchedule(kiosk.id, schedule))

        succ_mess = 'Kiosk settings successfully changed.'
        response = json_response_content('success', succ_mess)
        return JsonResponse(response)

    elif request.method == "GET":
        s = request.db_session
        kiosks = request.db_session.query(Kiosk)\
            .filter_by(company_id=company.id).all()
        response = json_response_content('success', 'Multi settings')
        response['data'].update({
            'timezones': s.query(Timezone).all(),
            'currencies': s.query(Currency).all(),
            'preauth_methods': s.query(PreauthMethod).all(),
            'no_internet_operations': s.query(NoInternetOperation).all(),
            'tariff_plans': company.tariff_plans,
            'payment_systems': company.payment_systems,
            'allLanguages': s.query(Language).all(),
            'kiosks': kiosks,
            'company_trailers':  company_trailers

        })
        return render(request, 'kiosk_multi_settings.html', response)
    else:
        return HttpResponseNotAllowed(('GET', 'POST'))