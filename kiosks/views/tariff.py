# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse

from Model import Kiosk, TariffPlan
from Model import TariffValue

from libs.validators.core import json_response_content
from acc.decorators import permission_required
from sqlalchemy import or_, and_


@login_required
@permission_required('price_plan_view')
def kiosk_tariff_plans(request, kiosk_id):
    kiosk = request.db_session.query(Kiosk).filter_by(id=kiosk_id).first()
    tariff_plans = kiosk.company.tariff_plans
    for tariff in tariff_plans:
        tariff.value = kiosk.actual_tariff_value(tariff)
    return render(request, 'kiosk_tariff_plans.html',
                  {'kiosk': kiosk,
                   'tariff_plans': tariff_plans})


@login_required
def tariff_values(request, kiosk_id, tariff_plan_id):

    kiosk = request.db_session.query(Kiosk).filter_by(id=kiosk_id).first()

    tariff_plan_values = request.db_session.query(TariffValue)\
        .filter_by(tariff_plan_id=tariff_plan_id)

    if request.method == "POST":
        first_night = request.POST.get('firstNight').replace(',', '.')
        next_night = request.POST.get('nextNight').replace(',', '.')
        sale = request.POST.get('sale').replace(',', '.')
        sun_night = request.POST.get('sunNight').replace(',', '.') if request.POST.get('sunNight') else None
        mon_night = request.POST.get('monNight').replace(',', '.') if request.POST.get('monNight') else None
        tue_night = request.POST.get('tueNight').replace(',', '.') if request.POST.get('tueNight') else None
        wed_night = request.POST.get('wedNight').replace(',', '.') if request.POST.get('wedNight') else None
        thu_night = request.POST.get('thuNight').replace(',', '.') if request.POST.get('thuNight') else None
        fri_night = request.POST.get('friNight').replace(',', '.') if request.POST.get('friNight') else None
        sat_night = request.POST.get('satNight').replace(',', '.') if request.POST.get('satNight') else None
        value_params = {
            'tariff_plan': tariff_plan_values.first().tariff_plan,
            'first_night': first_night, 
            'next_night': next_night, 
            'sale': sale,
            'sun_night': sun_night,
            'mon_night': mon_night,
            'tue_night': tue_night,
            'wed_night': wed_night,
            'thu_night': thu_night,
            'fri_night': fri_night,
            'sat_night': sat_night,
            'user': request.user
        }
        errors = kiosk.change_tariff(value_params)
        # if not errors:
        #     pass
            # tariff_plan_values = tariff_plan_values.filter_by(kiosk_id=kiosk_id).all()
            # return render(request, 'kiosk_tariff_values.html',
            #               {'kiosk_id': kiosk_id,
            #                'tariff_plan_id': tariff_plan_id,
            #                'tariff_values': tariff_plan_values})
        if errors:
            response = json_response_content('error', 'Something wrong with params of your tariff value')
            for error in errors:
                response['errors'].append(error)
            return JsonResponse(response)
        else:
            response = json_response_content('success', 'Tariff value edited successfully')
            return JsonResponse(response)


    tariff_plan = request.db_session.query(TariffPlan).filter_by(id=tariff_plan_id).first()
    tariff_plan_values = tariff_plan_values \
        .filter(or_(TariffValue.kiosk_id == kiosk_id, None == TariffValue.kiosk_id)) \
        .order_by(TariffValue.dt_end.desc())\
        .order_by(TariffValue.kiosk_id)\
        .all()
    for tpv in tariff_plan_values:
        tpv.level_of_assignment = "Current kiosk" if tpv.kiosk_id else "Whole company"
    return render(request, 'kiosk_tariff_values.html',
                  {'kiosk': kiosk,
                   'actual_tariff': kiosk.actual_tariff_value(tariff_plan),
                   'tariff_plan': tariff_plan,
                   'tariff_values': tariff_plan_values})


@login_required
@require_POST
def revert_tariff_values(request, kiosk_id, tariff_plan_id):
    import datetime
    from decimal import Decimal
    tariff_plan = request.db_session.query(TariffPlan).filter_by(id=tariff_plan_id).first()
    kiosk = request.db_session.query(Kiosk).filter_by(id=kiosk_id).first()
    tariff_value = kiosk.actual_tariff_value(tariff_plan)
    if tariff_value.kiosk_id:
        tariff_value.dt_end = datetime.datetime.utcnow()
        request.db_session.add(tariff_value)
        request.db_session.commit()
    response = json_response_content('success', 'Tariff value reverted successfully')
    response['redirect_url'] = reverse('kiosks.views.tariff_values', args=(Decimal(kiosk_id), Decimal(tariff_plan_id)))
    return JsonResponse(response)