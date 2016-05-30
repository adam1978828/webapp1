# -*- coding: utf-8 -*-
import json
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import pytz
from Model import LinkPoint, CompanyPaymentSystem, Company, FirstData
from acc.utils import process_archive
from libs.validators.core import json_response_content
from sqlalchemy.orm import joinedload
from acc.decorators import permission_required
from json import loads
from payments.forms import FirstDataForm

__author__ = 'D.Ivanets'


@permission_required('company_view_payments')
def payments(request):
    if request.user.is_focus:
        payment_accounts = request.db_session.query(CompanyPaymentSystem).all()
    else:
        payment_accounts = request.user.company.payment_systems

    return render_to_response('index.html', {'payment_accounts': payment_accounts},
                              context_instance=RequestContext(request))


@permission_required('company_add_payment')
def payments_add(request):
    return render_to_response('add.html', context_instance=RequestContext(request))


@permission_required('company_add_payment')
def payments_template(request):
    templates = ['', 'linkpoint', 'firstdata']
    path_id = int(request.POST.get('data', '1'))
    companies = request.db_session.query(Company).all()
    return render_to_response('pattern/%(path)s.html' % {'path': templates[path_id]},{'companies': companies},
                              context_instance=RequestContext(request))


@permission_required('company_add_payment')
@csrf_exempt
def ajax_upload_archive(request):
    """
    :param request:
    :return:
    """
    msg = 'No key_archive in request.FILES'
    if 'key_archive' in request.FILES:
        try:
            pay_id, username, password = process_archive(request.FILES['key_archive'])
        except Exception, e:
            response = json_response_content('error', 'Error occured during processing archive.')
            response['errors'].append({'field': 'archive', 'message': str(e) + ', ' + e.message})
            return JsonResponse(response, safe=False)
            # We have to process this result in some way

        ps = CompanyPaymentSystem()
        ps.payment_system_id = 1

        if request.user.is_focus:
            company_id = int(request.POST.get('f_company_id', 1))
            company = request.db_session.query(Company).filter_by(id=company_id).first()
        else:
            company = request.user.company

        ps.company = company
        ps.user = request.user
        lp = LinkPoint(username, password, pay_id)

        if request.db_session.query(CompanyPaymentSystem).options(joinedload('linkpoint')) \
                .filter(CompanyPaymentSystem.company == ps.company) \
                .filter(LinkPoint.username == username).first():
            lp.errors.append(
                {'field': 'username', 'message': 'LinkPoint account with such credentials already exists'})
        lp.company_payment_system = ps
        if lp.no_errors():
            request.db_session.add_all([lp, ps])
            response = json_response_content('success', 'Account was added successfully')
            response['data'] = {'username': username, 'password': password}
            # return HttpResponse(json.dumps({'error': False, 'username': username, 'password': password}),
            # content_type="application/json")
        else:
            response = json_response_content('error', 'Something wrong with your credentials')
            for error in lp.errors:
                # Here no errors are displayed because of format - change format in templates
                response['errors'].append(error)
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse(json_response_content('error', 'No archive given'), safe=False)


@permission_required('company_add_payment')
@require_POST
@csrf_exempt
def ajax_add_firstdata(request):
    """
    :param request:
    :return:
    """
    data = QueryDict(request.body)
    f = FirstDataForm(data)
    if not f.is_valid():
        response = json_response_content('error', 'Form is invalid')
        for key, value in f.errors.items():
            error = {'field': key, 'message': value}
            response['errors'].append(error)
            return JsonResponse(response, safe=False)
    data = f.cleaned_data
    ps = CompanyPaymentSystem()
    ps.payment_system_id = data.pop('ps_id')

    if request.user.is_focus:
        company_id = int(request.POST.get('f_company_id', 1))
        company = request.db_session.query(Company).get(company_id)
    else:
        company = request.user.company

    ps.company = company
    ps.user = request.user

    fd = FirstData(**data)
    fd.company_payment_system = ps
    request.db_session.add_all([fd, ps])

    response = json_response_content('success', 'Account added successfully')
    return JsonResponse(response, safe=False)

