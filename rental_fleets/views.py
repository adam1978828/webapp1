import re
import json
import datetime

from django.shortcuts import render_to_response, render
from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.views.decorators.http import require_POST, require_GET
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from sqlalchemy.orm.exc import NoResultFound

from Model import CompanyUpcTariffPlan, UPC, TariffPlan, Disk, Kiosk, Company, Slot, KioskSettings
from Model import Movie, MovieTranslation, MovieRating, Language, DisksView, Deal
from Model.base import ExtMixin

from WebApp.utils import alchemy_to_json
from libs.validators.core import json_response_content, validation_error
from libs.utils.json_functions import convert_json_keys_to_camelcase
from libs.wrappers.semantics3queries import get_upc
from acc.decorators import permission_required
from django.core.exceptions import PermissionDenied

from sqlalchemy import and_

from companies.views import check_company_id

from datatables import ColumnDT, DataTables


@login_required
@permission_required('price_plans_view_assignment')
def ajax_get_tariff_plans(request):
    p = request.POST
    print request.POST.__dict__
    c_id = p.get('company_id', '')
    print c_id
    if c_id:
        tariff_plans = request.db_session.query(TariffPlan).filter(TariffPlan.company_id == c_id).all()
        tariff_plans_list = []
        for tariff in tariff_plans:
            tariff_plans_list.append({"id": str(tariff.id), "name": tariff.name})

        return HttpResponse(json.dumps({'error': False, 'tariffPlans': tariff_plans_list}),
                            content_type="application/json")
    return HttpResponse(json.dumps({'error': True, 'src': None}),
                        content_type="application/json")


@login_required
@permission_required('price_plans_view_assignment')
def view_rental_fleets(request, company_id=None):
    r = check_company_id(request, company_id)
    company = r['company']
    upcs = request.db_session.query(UPC)
    res_per_time = 10
    companies = request.db_session.query(Company).all()
    rental_fleets = request.db_session.query(CompanyUpcTariffPlan).filter_by(company=company).all()
    tariff_plans = request.db_session.query(TariffPlan).filter_by(company=company).all()

    return render_to_response('rental_fleets_index.html', {
        'company': company,
        'companies': companies,
        'filter_company': True,
        'rentalFleets': rental_fleets,
        'tariffPlans': tariff_plans,
        'upcs_amount': upcs.count() - res_per_time,
        'upcs': upcs.limit(res_per_time)
    }, context_instance=RequestContext(request))


@login_required
@permission_required('price_plans_view_assignment')
def index(request):
    upcs = request.db_session.query(UPC)
    res_per_time = 10
    if request.method == 'GET':

        if request.user.is_focus:
            companies = request.db_session.query(Company).all()
            rental_fleets = request.db_session.query(CompanyUpcTariffPlan).all()
            tariff_plans = request.db_session.query(TariffPlan).all()
        else:
            companies = []
            rental_fleets = request.db_session.query(CompanyUpcTariffPlan).filter_by(company=request.user.company).all()
            tariff_plans = request.db_session.query(TariffPlan).filter_by(company=request.user.company).all()

        return render_to_response('rental_fleets_index.html', {
            'companies': companies,
            'rentalFleets': rental_fleets,
            'tariffPlans': tariff_plans,
            'upcs_amount': upcs.count() - res_per_time,
            'upcs': upcs.limit(res_per_time)
        }, context_instance=RequestContext(request))
    elif request.method == 'POST':
        if 'price_plans_add_assignment' not in request.user.rights:
            raise PermissionDenied

        if request.user.is_focus:
            company_id = int(request.POST.get('f_company_id', 1))
        else:
            company_id = int(request.user.company.id)

        upc_link = request.POST.get('upcLink', -1)

        if request.user.is_focus:
            company_upc_tariff_plan = request.db_session.query(CompanyUpcTariffPlan).\
                filter(and_(CompanyUpcTariffPlan.company_id == company_id, CompanyUpcTariffPlan.upc_link == upc_link))
        else:
            company_upc_tariff_plan = request.db_session.query(CompanyUpcTariffPlan).\
                filter(and_(CompanyUpcTariffPlan.company_id == company_id, CompanyUpcTariffPlan.upc_link == upc_link))

        if company_upc_tariff_plan.count():
            company_upc_tariff_plan = company_upc_tariff_plan.first()
        else:
            company_upc_tariff_plan = CompanyUpcTariffPlan()

            if request.user.is_focus:
                company_upc_tariff_plan.company_id = company_id
            else:
                company_upc_tariff_plan.company_id = request.user.company.id

            company_upc_tariff_plan.upc_link = upc_link

        company_upc_tariff_plan.tariff_plan_id = request.POST.get('tariffPlanId', -1)

        if company_upc_tariff_plan.no_errors():
            request.db_session.add(company_upc_tariff_plan)
            request.db_session.commit()

            if request.user.is_focus:
                rental_fleets = request.db_session.query(CompanyUpcTariffPlan).\
                    filter(CompanyUpcTariffPlan.company_id == company_id).all()
                tariff_plans = request.db_session.query(TariffPlan).filter(TariffPlan.company_id == company_id).all()
            else:
                rental_fleets = request.db_session.query(CompanyUpcTariffPlan).\
                    filter_by(company=request.user.company).all()
                tariff_plans = request.db_session.query(TariffPlan).filter_by(company_id=company_id).all()

            filter_company = request.POST.get('filter_company', '')
            if filter_company:
                return HttpResponseRedirect(reverse('rental_fleets.views.view_rental_fleets', args=(filter_company,)))

            companies = request.db_session.query(Company).all()
            return render_to_response('rental_fleets_index.html', {
                'companies': companies,
                'rentalFleets': rental_fleets,
                'tariffPlans': tariff_plans,
                'upcs_amount': upcs.count() - res_per_time,
                'upcs': upcs.limit(res_per_time)
            }, context_instance=RequestContext(request))
        else:
            if company_upc_tariff_plan in request.db_session:
                request.db_session.expunge(company_upc_tariff_plan)
            response = json_response_content('error', 'Can not save your rental fleet')
            for error in company_upc_tariff_plan.errors:
                response['errors'].append(error)
            return JsonResponse(response)
    else:
        raise Http404


# Was neccessary when UPC was dropdown for live search.
# Leave it for now - maybe smth will change again with this field ;)
@login_required
def upc_search(request):
    """
    UPC live search
    """
    if request.method == 'GET':
        res_per_time = 10
        upc_part = request.GET.get('upcLink', '')
        upc_result = request.db_session.query(UPC.upc).filter(UPC.upc.contains(upc_part))
        return JsonResponse({
            'query': upc_part,
            'upcs': upc_result.limit(res_per_time).all(),
            'upcs_amount': upc_result.count() - res_per_time,
        })
    else:
        raise Http404


@login_required
def show_disk(request, disk_rf_id):
    if disk_rf_id:
        query = request.db_session.query(Disk).filter_by(rf_id=disk_rf_id)
        if request.user.is_company:
            query = query.filter_by(company=request.user.company)
        disk = query.first()
        if not disk:
            raise PermissionDenied
        return render(request, 'disk.html', {'disk': disk})
    else:
        raise Http404


@login_required
@require_GET
@permission_required('rental_view_disk')
def disks(request):
    return render(request, 'rental_fleets_disks.html', {})


def _add_href_in_disk__rf_id(val):
    return '<a href="{0}">{1}</a>'.format(reverse('rental_fleets.views.show_disk', args=(val,)), val)


def _add_href_in_disk__deal(deal):

    output = '<a href="{0}">{{0}} ({1})</a>'
    url = reverse('deals.views.deal_by_id', args=(deal.id,))
    kiosk_alias = deal.kiosk_start.settings.alias
    return output.format(url, kiosk_alias)


def _add_href_in_upc(val):
    return '<a href="{0}">{1}</a>'.format(reverse('rental_fleets.views.show_upc', args=(val,)), val)


def _unknown_column_value(val):
    return val if val is not None else '-'


def _date_column(val):
    return val.strftime('%m/%d/%y') if val is not None else '-'


def _unknown_cash_value(val):
    return "${0}".format(val) if val is not None else '-'


@login_required
def json_disks(request):
    columns = list()

    if request.user.is_focus:
        columns.append(ColumnDT('company_name', filter=_unknown_column_value))

    columns.append(ColumnDT('disk_rfid', filter=_add_href_in_disk__rf_id))
    columns.append(ColumnDT('disk_upc', filter=_add_href_in_upc))
    columns.append(ColumnDT('movie_name', filter=_unknown_column_value))
    columns.append(ColumnDT('disk_format', filter=_unknown_column_value))
    columns.append(ColumnDT('movie_release_date', filter=_date_column))
    columns.append(ColumnDT('movie_dvd_release_date', filter=_date_column))
    columns.append(ColumnDT('disk_state', filter=_unknown_column_value))

    columns.append(ColumnDT('kiosk_alias', filter=_unknown_column_value))
    columns.append(ColumnDT('kiosk_slot_number', filter=_unknown_column_value))

    columns.append(ColumnDT('rent_days', filter=_unknown_column_value))
    columns.append(ColumnDT('deal_first_night_rent_charge', filter=_unknown_cash_value))
    # columns.append(ColumnDT('deal_next_night_rent_charge', filter=_unknown_cash_value))
    columns.append(ColumnDT('deal_sale_charge', filter=_unknown_cash_value))
    columns.append(ColumnDT('deal_total_amount', filter=_unknown_cash_value))

    query = request.db_session.query(DisksView)
    if request.user.is_company:
        query = query.filter_by(company_id=request.user.company.id)
    row_table = DataTables(request, DisksView, query, columns)
    response = row_table.output_result()

    return JsonResponse(response)


@login_required
def show_upc(request, upc):
    if upc:
        upc = request.db_session.query(UPC).filter(UPC.upc == upc).first()
        t_p = request.db_session.query(TariffPlan)\
                     .join(CompanyUpcTariffPlan)\
                     .filter_by(company=request.user.company)\
                     .filter_by(upc=upc).first()
        # for raw in res:
        #     d = Disk()
        #     d.rf_id = str(raw[0])
        #     d.upc_link = str(raw[1])
        #     print raw[0], raw[1],
        #     try:
        #         request.db_session.add(d)
        #         request.db_session.commit()
        #         print '+'
        #     except Exception as ex:
        #         request.db_session.rollback()
        #         print ex.message
        return render(request, 'upc.html', {'upc': upc, 'movie': upc.movie, 'tariff_plan': t_p})
    else:
        raise Http404


@login_required
def upc_detailed(request):
    def render_tariff_plan_template(upc_code):
        from django.template.response import TemplateResponse
        t_p = request.db_session.query(TariffPlan).\
            join(CompanyUpcTariffPlan).\
            filter_by(company=request.user.company).\
            filter_by(upc=upc_code).first()
        html = TemplateResponse(request, 'upc_detailed.html', {'upc': upc_code, 'movie': upc_code.movie, 'tariff_plan': t_p})
        html.render()
        return html

    if request.method == "GET" and request.is_ajax():
        upc_link = request.GET.get('upcLink')
        if upc_link:
            upc = request.db_session.query(UPC).filter(UPC.upc == upc_link).first()
            if upc:
                response = json_response_content('success', 'UPC %s was found' % upc_link)
                response['data'] = {
                    'html': render_tariff_plan_template(upc).content
                }
            else:
                try:
                    results = get_upc(upc_link)
                except Exception, e:
                    return JsonResponse(json_response_content('error', e.message))
                if results and results[u'results_count'] > 0:
                    result = results[u'results'][0]
                    title = re.split('( \()*\)*', result[u'name'])
                    # for example: name == "Live Die Repeat:Edge of Tomorrow (Blu-ray + DVD) (2014)"
                    search_obj = re.search("(\(*\d+\)*)", result[u'name'])  # get "(2014)" from name
                    name = title[0]
                    year = search_obj.groups()[-1] if search_obj else None  # year = last element from tuple
                    year = year.strip('()')  # strip "(",  ")" from verified string
                    movie = request.db_session.query(Movie).join(MovieTranslation)\
                        .filter(MovieTranslation.name.ilike('%{}%'.format(name))).first()
                    if not movie:
                        length = int(round(float(result.get(u'length', 0))))
                        if year:
                            year = int(year)
                        language = request.db_session.query(Language).filter_by(name=result[u'language']).first()
                        rated, rating = results.get(u'features', {}).get(u'Rated', None), None
                        if rated:
                            # rate = rated.split(' ')[0]
                            rating = request.db_session.query(MovieRating)\
                                .filter(MovieRating.value.ilike(rated.lower())).first()
                            request.db_session.add(rating)
                        mt = MovieTranslation(name, lang=language)
                        movie = Movie(length, year, rating, movie_translation=[mt])
                        request.db_session.add_all([mt, movie])
                    upc = UPC(result[u'upc'], movie)
                    request.db_session.add(upc)
                    request.db_session.commit()
                    response = json_response_content('success',
                                                     "UPC %s was successfully created" % str(result[u'upc']))
                    response['data'] = {
                        'html': render_tariff_plan_template(upc).content
                    }
                else:
                    response = json_response_content('error', 'Can not find UPC %s' % upc_link)
        else:
            response = json_response_content('error', 'UPC link not given')
        return JsonResponse(response)
    else:
        raise Http404


@login_required
@permission_required('rental_add_disk')
def add_disk(request):
    """ Responsible for assigning disks to upc codes and companies.
    """
    # Request for HTML page
    if request.method == "GET":
        per_time = 10
        upc_list = request.db_session.query(UPC).limit(per_time)
        if request.user.is_focus:
            companies = request.db_session.query(Company).all()
        else:
            companies = []

        render_data = {
            'upcs': upc_list,
            'companies': companies
        }

        return render(request, 'rental_fleet_add_disk.html', render_data)

    # Post assigning data
    elif request.method == 'POST':
        if request.user.is_focus:
            company_id = int(request.POST.get('f_company_id', 1))
        else:
            company_id = request.user.company_id

        upc_link = request.POST.get('upcLink', None)
        upc = request.db_session.query(UPC) \
            .filter_by(upc=upc_link).first()

        rf_id = request.POST.get('rfId', None)

        # If all required data presented in request
        if upc and rf_id:

            disk = request.db_session.query(Disk).get(rf_id)

            # If this is a new disk:
            if not disk:

                disk = Disk(rf_id=rf_id, upc=upc)
                disk.company_id = company_id

                if disk.no_errors():
                    request.db_session.add(disk)
                    request.db_session.commit()

                    message = 'Disk {} was successfully mapped to UPC {}' \
                              ''.format(rf_id, upc_link)
                    data = alchemy_to_json(disk)
                    data = convert_json_keys_to_camelcase(data)

                    response = json_response_content('success', message)
                    response['data']['disk'] = data
                else:
                    if disk in request.db_session:
                        request.db_session.expunge(disk)
                    message = 'Some errors occured during adding disk'
                    response = json_response_content('error', message)
                    response['errors'] = [error for error in disk.errors]

            # Such disk exists
            else:
                old_upc = disk.upc
                if old_upc:
                    message = 'Disk with such RFID already exists for UPC {}' \
                              ''.format(old_upc.upc)
                    response = json_response_content('warning', message)
                    if old_upc.upc != upc.upc or company_id != disk.company_id:
                        company_change = company_id != disk.company_id
                        html = TemplateResponse(
                            request,
                            'modals/already_mapped_rfid.html',
                            {'old_upc': old_upc,
                             'new_upc': upc,
                             'company_change': company_change}
                        )
                        html.render()
                        response['message'] += '. Reassign?'
                        response['data'] = {
                            'modal_html': html.content
                        }
                    elif not request.user.is_focus and \
                            company_id != disk.company_id:
                        message = 'Disk with such RFID already exists and ' \
                                  'belongs to another company.'
                        response = json_response_content('error', message)

                else:
                    disk.upc = upc
                    request.db_session.add(disk)
                    request.db_session.commit()
                    message = 'Disk {} was successfully mapped to UPC {}' \
                              ''.format(rf_id, upc_link)
                    response = json_response_content('success', message)
        else:
            if not upc_link:
                message = 'Both RFID and UPC are required'
                response = json_response_content('warning', message)
            else:
                response = json_response_content('error', 'Wrong UPC!')
        return JsonResponse(response)


@login_required
@require_POST
def reassign_disk_upc(request, disk_rf_id, upc):
    """ When user tries to reassign disc upc code, there is a prompt, that asks
    permission to change UPC code. That prompt calls this view.
    """
    disk = request.db_session.query(Disk)\
        .filter_by(rf_id=disk_rf_id)
    disk = disk.first()

    if disk:
        upc = request.db_session.query(UPC)\
            .filter_by(upc=upc).first()
        disk.upc = upc
        if request.user.is_focus:
            company_id = int(request.POST.get('f_company_id', 1))
            disk.company_id = company_id
        elif request.user.is_company:
            disk.company_id = request.user.company_id
        request.db_session.add(disk)
        request.db_session.commit()
        message = 'UPC {} was successfully reassigned to disk {}' \
                  ''.format(upc.upc, disk_rf_id)
        response = json_response_content('success', message)

        movie_info = "{0}({1})/{2}".format(upc.movie.get_name,
                                           upc.format.name,
                                           upc.movie.release_year)
        response['data']['movieInfo'] = movie_info
        return JsonResponse(response)
    else:
        message = 'No disk with RFID {}'.format(disk_rf_id)
        return JsonResponse(json_response_content('error', message))


@login_required
def check_upc_price_plan(request, upc):
    upc_obj = request.db_session.query(UPC).filter_by(upc=upc).first()
    if upc_obj.tariff_plan:
        return JsonResponse(json_response_content('success', 'Tariff plan is assigned'))
    else:
        from django.template.response import TemplateResponse
        tariff_plans = request.db_session.query(TariffPlan)\
            .filter(TariffPlan.company_id == request.user.company_id)\
            .all()
        response = json_response_content('warning', 'Please assign tariff plan before going on.')
        html = TemplateResponse(request, 'modals/add_disk_priceplan_issue.html',
                                {'upc': upc_obj, 'tariffPlans': tariff_plans})
        html.render()
        response['data'] = {
            'modal_html': html.content
        }
        return JsonResponse(response)


@login_required
@require_POST
def add_upc_price_plan(request, upc):
    company_upc_tariff_plan = CompanyUpcTariffPlan()
    company_upc_tariff_plan.company_id = request.user.company.id
    company_upc_tariff_plan.upc_link = upc
    tariff_plan_id = request.POST.get('tariffPlanId')
    if not tariff_plan_id:
        return JsonResponse(json_response_content('error', 'Tariff plan is no specified'))
    try:
        tariff_plan = request.db_session.query(TariffPlan)\
            .filter(TariffPlan.id == tariff_plan_id)\
            .filter(TariffPlan.company == request.user.company).one()
        company_upc_tariff_plan.tariff_plan_id = tariff_plan.id
    except NoResultFound:
        return JsonResponse(json_response_content('error', 'Cannot assign tariff plan to UPC'))

    if company_upc_tariff_plan.no_errors():
        tariff_plan = request.db_session.query(TariffPlan).filter_by(id=tariff_plan_id)\
            .filter(TariffPlan.company == request.user.company).first()
        response = json_response_content('success', 'Tariff plan ' + tariff_plan.name +
                                                    ' was successfully assigned to UPC ' + upc)
        request.db_session.add(company_upc_tariff_plan)
        request.db_session.commit()
    else:
        if company_upc_tariff_plan in request.db_session:
            request.db_session.expunge(company_upc_tariff_plan)
        response = json_response_content('error', 'Cannot assign tariff plan to UPC')
        for error in company_upc_tariff_plan.errors:
            response['errors'].append(error)
    return JsonResponse(response)


@login_required
@require_GET
@permission_required('rental_view_disk')
def disks_out(request):
    return render(request, 'rental_fleet_disks_out.html', {})


@login_required
def json_disks_out(request):
    columns = list()
    if request.user.is_focus:
        columns.append(ColumnDT('company_name', filter=_unknown_column_value))
    columns.append(ColumnDT('disk_rfid', filter=_add_href_in_disk__rf_id))
    columns.append(ColumnDT('disk_upc', filter=_add_href_in_upc))
    columns.append(ColumnDT('movie_name', filter=_unknown_column_value))
    columns.append(ColumnDT('disk_format', filter=_unknown_column_value))
    columns.append(ColumnDT('disk_state', filter=_unknown_column_value))
    columns.append(ColumnDT('deal_start_date', filter=_date_column))
    columns.append(ColumnDT('kiosk_rented_alias', filter=_unknown_column_value))

    query = request.db_session.query(DisksView).filter_by(is_in_rent=1)

    if request.user.is_company:
        query = query.filter_by(company_id=request.user.company.id)

    row_table = DataTables(request, DisksView, query, columns)
    response = row_table.output_result()

    return JsonResponse(response)