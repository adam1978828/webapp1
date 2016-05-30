# from django.shortcuts import render
# , Http404, HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from Model import TariffPlan, TariffValue, Company
from django.contrib.auth.decorators import login_required
from libs.validators.core import json_response_content
from json import loads
from Model.base import ExtMixin
from datetime import datetime
from acc.decorators import permission_required
from django.core.exceptions import PermissionDenied

__author__ = 'D.Kalpakchi'


# Create your views here.
@login_required
@permission_required('price_plan_add')
def add_price_plan(request):
    if request.method == 'GET':
        return render_to_response('priceplans/get.html',
            {'mode': 'add'},
            context_instance=RequestContext(request))
    elif request.method == 'POST':
        mode = request.POST.get('mode')
        if mode == 'save':
            data = loads(request.POST.get('data'))
            fields = data['priceField']
            if request.user.is_focus:
                company = request.db_session.query(Company).filter_by(id=int(fields['f_company_id'])).first()
            else:
                company = request.user.company
            name = fields['name']
            first_night = fields['firstNight']
            next_night = fields['nextNight']
            sale = fields['sale']
            sun_night = fields['sunNight']
            mon_night = fields['monNight']
            tue_night = fields['tueNight']
            wed_night = fields['wedNight']
            thu_night = fields['thuNight']
            fri_night = fields['friNight']
            sat_night = fields['satNight']
            tariff_plan = TariffPlan(name, company)
            tariff_plan.user = request.user
            if request.db_session.query(TariffPlan)\
                .filter_by(company_id=company.id).filter_by(
                    name=name).first():
                tariff_plan.errors.append(
                    {'field': 'name', 'message': ("Tariff plan named %s already exists. Change name, please" % name)})
            tariff_value = TariffValue(tariff_plan)
            tariff_value.first_night = first_night.replace(',', '.')
            tariff_value.next_night = next_night.replace(',', '.')
            tariff_value.sale = sale.replace(',', '.')
            tariff_value.sun_night = sun_night.replace(',', '.') if sun_night else None
            tariff_value.mon_night = mon_night.replace(',', '.') if mon_night else None
            tariff_value.tue_night = tue_night.replace(',', '.') if tue_night else None
            tariff_value.wed_night = wed_night.replace(',', '.') if wed_night else None
            tariff_value.thu_night = thu_night.replace(',', '.') if thu_night else None
            tariff_value.fri_night = fri_night.replace(',', '.') if fri_night else None
            tariff_value.sat_night = sat_night.replace(',', '.') if sat_night else None
            tariff_value.user = request.user
            if tariff_value.first_night >= tariff_value.sale:
                tariff_value.errors.append({
                    'field': 'firstNight',
                    'message': 'First night tariff value must be less than sale tariff value'
                })
            if tariff_value.next_night >= tariff_value.sale:
                tariff_value.errors.append({
                    'field': 'nextNight',
                    'message': 'Next night tariff value must be less than sale tariff value'
                })
            if tariff_plan.no_errors() and tariff_value.no_errors():
                if tariff_value.no_errors():
                    request.db_session.add_all([tariff_plan, tariff_value])
                    request.db_session.commit()
                    response = json_response_content(
                        'success', 'Tariff plan %s was successfully added' % name)
                else:
                    if tariff_plan in request.db_session:
                        request.db_session.expunge(tariff_plan)
                    if tariff_value in request.db_session:
                        request.db_session.expunge(tariff_value)
                    response = json_response_content(
                        'error', 'Errors occured while adding tariff plan')
            else:
                if tariff_plan in request.db_session:
                    request.db_session.expunge(tariff_plan)
                if tariff_value in request.db_session:
                    request.db_session.expunge(tariff_value)
                response = json_response_content(
                    'error', 'Errors occured while adding tariff plan')
            for error in tariff_plan.errors:
                response['errors'].append(error)
            for error in tariff_value.errors:
                response['errors'].append(error)
            return JsonResponse(response, safe=False)
        elif mode == 'add':
            if request.user.is_focus:
                companies = request.db_session.query(Company).all()
            elif request.user.is_company:
                companies = []
            return render_to_response('priceplans/add.html',
                                      {'mode': 'add', 'companies': companies},
                                      context_instance=RequestContext(request))


@login_required
@permission_required('price_plan_edit')
def edit_price_plan(request, tariff_plan_id):
    tariff_plan = request.db_session.query(TariffPlan).filter(TariffPlan.id == tariff_plan_id).first()
    if request.user.is_company:
        if tariff_plan.company_id != request.user.company.id:
            raise PermissionDenied
    if request.method == 'GET':
        return render_to_response('priceplans/get.html',
            {'mode': 'edit', 'tariff_plan': tariff_plan},
            context_instance=RequestContext(request))
    elif request.method == 'POST':
        mode = request.POST.get('mode')
        if mode == 'save':
            data = loads(request.POST.get('data'))
            fields = data['priceField']
            company = request.user.company
            name = fields['name']
            first_night = fields['firstNight']
            next_night = fields['nextNight']
            sale = fields['sale']
            sun_night = fields['sunNight']
            mon_night = fields['monNight']
            tue_night = fields['tueNight']
            wed_night = fields['wedNight']
            thu_night = fields['thuNight']
            fri_night = fields['friNight']
            sat_night = fields['satNight']
            tariff_plan.name = name
            if request.user.is_focus:
                tariff_plan.company_id = int(fields['f_company_id'])
            current_tariff = tariff_plan.last_tariff_value
            current_tariff.dt_end = datetime.utcnow()
            tariff_value = TariffValue(tariff_plan)
            tariff_value.first_night = first_night.replace(',', '.')
            tariff_value.next_night = next_night.replace(',', '.')
            tariff_value.sale = sale.replace(',', '.')
            tariff_value.sun_night = sun_night.replace(',', '.') if sun_night else None
            tariff_value.mon_night = mon_night.replace(',', '.') if mon_night else None
            tariff_value.tue_night = tue_night.replace(',', '.') if tue_night else None
            tariff_value.wed_night = wed_night.replace(',', '.') if wed_night else None
            tariff_value.thu_night = thu_night.replace(',', '.') if thu_night else None
            tariff_value.fri_night = fri_night.replace(',', '.') if fri_night else None
            tariff_value.sat_night = sat_night.replace(',', '.') if sat_night else None
            tariff_value.user = request.user
            if tariff_value.first_night >= tariff_value.sale:
                tariff_value.errors.append({
                    'field': 'firstNight',
                    'message': 'First night tariff value must be less than sale tariff value'
                })
            if tariff_value.next_night >= tariff_value.sale:
                tariff_value.errors.append({
                    'field': 'nextNight',
                    'message': 'Next night tariff value must be less than sale tariff value'
                })
            if tariff_plan.no_errors() and tariff_value.no_errors():
                if tariff_value.no_errors():
                    tariff_plan.last_tariff_value.dt_end = datetime.utcnow()
                    request.db_session.add_all([tariff_plan, tariff_value])
                    request.db_session.commit()
                    response = json_response_content(
                        'success', 'Tariff plan %s was successfully updated' % name)
                else:
                    if tariff_plan in request.db_session:
                        request.db_session.expunge(tariff_plan)
                    if tariff_value in request.db_session:
                        request.db_session.expunge(tariff_value)
                    response = json_response_content(
                        'error', 'Errors occured while updating tariff plan')
            else:
                if tariff_plan in request.db_session:
                    request.db_session.expunge(tariff_plan)
                if tariff_value in request.db_session:
                    request.db_session.expunge(tariff_value)
                response = json_response_content(
                    'error', 'Errors occured while updating tariff plan')
            for error in tariff_plan.errors:
                response['errors'].append(error)
            for error in tariff_value.errors:
                response['errors'].append(error)
            return JsonResponse(response, safe=False)
        elif mode == 'edit':
            if request.user.is_focus:
                companies = request.db_session.query(Company).all()
            elif request.user.is_company:
                companies = []
            return render_to_response('priceplans/add.html', 
                                      {'mode': 'edit', 'tariff_plan': tariff_plan, 'companies': companies},
                                      context_instance=RequestContext(request))


@login_required
@permission_required('price_plan_view')
def show_price_plan(request, tariff_plan_id):
    tariff_plan = request.db_session.query(TariffPlan)\
        .filter(TariffPlan.id == tariff_plan_id).first()
    if tariff_plan.company_id != request.user.company.id:
        raise PermissionDenied
    if request.method == 'GET':
        return render_to_response('priceplans/get.html',
                                  {'mode': 'show', 'tariff_plan': tariff_plan},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        mode = request.POST.get('mode')
        if mode == 'show':
            return render_to_response('priceplans/add.html',
                                      {'mode': 'show', 'tariff_plan': tariff_plan},
                                      context_instance=RequestContext(request))


@login_required
@permission_required('price_plan_view')
def all_price_plans(request):
    if request.method == 'GET':
        company = request.user.company
        query = request.db_session.query(TariffPlan)
        if request.user.is_company:
            query = query.filter_by(company_id=company.id)
        tariff_plans = query.all()
        return render_to_response('priceplans/index.html',
                                  {'tariff_plans': tariff_plans},
                                  context_instance=RequestContext(request))
