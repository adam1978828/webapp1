import datetime, pytz

from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from Model import Deal, DealType, TariffValue, DealsView
from libs.utils.datetime_functions import to_utc
from libs.validators.core import json_response_content
from acc.decorators import permission_required

from datatables import ColumnDT, DataTables

__author__ = 'D.Kalpakchi'


def _unknown_column_value(val):
    return val if val else '-'


def _deal_id_btn(val):
    return '<a href="/deals/deal/{0}/" class="button small grey tooltip" data-gravity=\'s\' original title="Edit"><i class="icon-pencil"></i></a>'.format(val)


def _date_column(val):
    return val.strftime("%m/%d/%y") if val else '-'


def _card_filter(val):
    name, n1, n2 = val.split(':')
    name = _unknown_column_value(name)
    number = str(int(n2[:4] + n1[:4] + n2[4:] + n1[4:]) / 3)
    return '%s (%s...%s)' % (name, number[:4], number[-4:])


def _unknown_release_date(val):
    if isinstance(val, datetime.datetime):
        return val.strftime('%b %d, %Y')
    return val if val is not None else '-'


def _unknown_datetime(val):
    if isinstance(val, datetime.datetime):
        return val.strftime('%x<br>%X')
    return val if val is not None else '-'


def _deal_id_filter(val):
    return val[:8]


def _clickable_class(val):
    return 'dt-row-click'


DEALS_DT_COLUMNS = list()
DEALS_DT_COLUMNS.append(ColumnDT('deal_id', mData='DT_RowId'))
DEALS_DT_COLUMNS.append(ColumnDT('deal_id', mData='deal_id', filter=_deal_id_filter))
DEALS_DT_COLUMNS.append(ColumnDT('card_cardholder_name_n1_n2', mData='card_cardholder_name_n1_n2', filter=_card_filter))
DEALS_DT_COLUMNS.append(ColumnDT('movie_translation_name', mData='movie_translation_name', filter=_unknown_column_value))
DEALS_DT_COLUMNS.append(ColumnDT('deal_status_alias', mData='deal_status_alias', filter=_unknown_column_value))
DEALS_DT_COLUMNS.append(ColumnDT('deal_dt_start', mData='deal_dt_start', filter=_unknown_column_value))
DEALS_DT_COLUMNS.append(ColumnDT('deal_dt_end', mData='deal_dt_end', filter=_unknown_column_value))
DEALS_DT_COLUMNS.append(ColumnDT('kiosk_settings_start_alias', mData='kiosk_settings_start_alias', filter=_unknown_column_value))
DEALS_DT_COLUMNS.append(ColumnDT('company_name', mData='company_name', filter=_unknown_column_value))


@login_required
@permission_required('transactions_view')
def all_deals(request):
    return render(request, 'deals.html', {})


@login_required
def json_deals(request, disk_rf_id=None):
    columns = list()
    columns.append(ColumnDT('deal_id', filter=_deal_id_filter))
    columns.append(ColumnDT('card_cardholder_name_n1_n2', filter=_card_filter))
    columns.append(ColumnDT('movie_translation_name', filter=_unknown_column_value))
    columns.append(ColumnDT('deal_status_alias', filter=_unknown_column_value))
    columns.append(ColumnDT('deal_dt_start', filter=_unknown_datetime))
    columns.append(ColumnDT('deal_dt_end', filter=_unknown_datetime))
    columns.append(ColumnDT('kiosk_settings_start_alias', filter=_unknown_column_value))
    columns.append(ColumnDT('kiosk_settings_end_alias', filter=_unknown_column_value))
    if request.user.is_focus:
        columns.append(ColumnDT('company_name', filter=_unknown_column_value))
    columns.append(ColumnDT('deal_id', mData='DT_RowId'))
    columns.append(ColumnDT('deal_id', mData='DT_RowClass', filter=_clickable_class))

    query = request.db_session.query(DealsView)
    if disk_rf_id:
        query = query.filter_by(deal_rf_id=disk_rf_id)
    if request.user.is_company:
        query = query.filter_by(company_id=request.user.company.id)

    return JsonResponse(DataTables(request, DealsView, query, columns).output_result())


@login_required
@permission_required('transactions_view')
def deal_by_id(request, deal_id):
    if request.method == "GET":
        query = request.db_session.query(Deal).filter_by(id=deal_id)
        if request.user.is_company:
            query = query.filter_by(company = request.user.company)
        deals = query.all()
        return render(request, 'deal_one.html', {'deals': deals})
    else:
        raise Http404


@login_required
@permission_required('transactions_view')
def show_deal(request, deal_id):
    if request.method == "GET":
        if request.user.is_focus:
            deal = request.db_session.query(Deal).filter_by(id=deal_id).first()
        elif request.user.is_company:
            deal = request.db_session.query(Deal).filter_by(id=deal_id, company = request.user.company).first()
        # Just before the OverRent will be handled
        deal_types = request.db_session.query(DealType).filter(DealType.id != 3).all()
        return render(request, 'deals_show.html', {'deal': deal, 'deal_types': deal_types})
    else:
        raise Http404


@login_required
@require_POST
def finish_deal(request, deal_id):
    if request.user.is_focus:
        deal = request.db_session.query(Deal).filter_by(id=deal_id).first()
    elif request.user.is_company:
        deal = request.db_session.query(Deal).filter_by(id=deal_id, company = request.user.company).first()
    return_type = request.POST.get('type')
    deal.dt_end = to_utc(request.POST.get('dtEnd'), deal.kiosk_start.settings.timezone.name)
    deal.deal_status_id = 521 if return_type == '1' else 522
    deal.disk.state_id = 0
    if deal.no_errors():
        request.db_session.add(deal)
        request.db_session.commit()
        response = json_response_content('success', 'Transaction finished successfully')
        response['redirect_url'] = reverse('deals.views.all_deals')
    else:
        response = json_response_content('error', 'Some errors occured during finishing transactions')
        for error in deal.errors:
            response['errors'].append(error)
    return JsonResponse(response)


@login_required
@require_POST
@csrf_exempt
def finish_deal_void(request, deal_id):
    if request.user.is_focus:
        deal = request.db_session.query(Deal).filter_by(id=deal_id).first()
    elif request.user.is_company:
        deal = request.db_session.query(Deal).filter_by(id=deal_id, company = request.user.company).first()
    deal.dt_end = datetime.datetime.utcnow()
    deal.total_amount = 0
    deal.force_total_amount = True
    deal.deal_status_id = 521
    deal.disk.state_id = 0
    if deal.no_errors():
        request.db_session.add(deal)
        request.db_session.commit()
        response = json_response_content('success', 'Transaction is finishing. Please wait up to 30 seconds.')
        response['redirect_url'] = reverse('deals.views.all_deals')
    else:
        response = json_response_content('error', 'Some errors occured during finishing transactions')
        for error in deal.errors:
            response['errors'].append(error)
    return JsonResponse(response)


@login_required
@require_POST
@permission_required('transactions_edit')
def manual_change(request, deal_id):
    if request.user.is_focus:
        deal = request.db_session.query(Deal).filter_by(id=deal_id).first()
    elif request.user.is_company:
        deal = request.db_session.query(Deal).filter_by(id=deal_id, company = request.user.company).first()
    current_tariff_value = deal.tariff_value
    current_tariff_plan = current_tariff_value.tariff_plan
    first_night = request.POST.get('firstNight', None)
    next_night = request.POST.get('nextNight', None)
    deal_type_id = request.POST.get('dealTypeId', None)
    total_days = request.POST.get('totalDays', None)
    total_amount = request.POST.get('totalAmount', None)
    sale = request.POST.get('sale', None)
    
    if deal_type_id:
        deal.deal_type_id = int(deal_type_id)
    deal.deal_status_id = 701 if deal.deal_type_id == 1 else 702
    
    if total_amount:
        deal.total_amount = total_amount
        deal.force_total_amount = True
    else:
        deal.force_total_amount = False
        if sale:
            tariff_value = TariffValue.copy(current_tariff_value)
            tariff_value.sale = sale
        else:
            kiosk = deal.kiosk_end if deal.kiosk_end else deal.kiosk_start
            if total_days:
                # validation of string - make
                deal.total_days = int(total_days)
            if first_night:
                tariff_value = TariffValue.copy(current_tariff_value)
                tariff_value.first_night = first_night
            if next_night:
                if 'tariff_value' not in locals():
                    tariff_value = TariffValue.copy(current_tariff_value)
                    tariff_value.next_night = next_night
        
        if 'tariff_value' in locals():
            time = datetime.datetime.utcnow()
            tariff_value.dt_start = time
            tariff_value.dt_modify = time
            tariff_value.dt_end = time
            deal.dt_end = time
            if tariff_value.no_errors():
                request.db_session.add(tariff_value)
            else:
                response = json_response_content('error', 'Something went wrong')
                for error in tariff_value.errors:
                    response['errors'].append(error)
            deal.tariff_value = tariff_value

        deal.total_amount = deal.calculate_amount()

    if deal.no_errors():
        request.db_session.add(deal)
        request.db_session.commit()
        response = json_response_content('success', 'Deal was successfully change manually')
        response['data']['status'] = deal.deal_status.alias
    else:
        if 'response' not in locals():
            response = json_response_content('error', 'Something went wrong')
        for error in tariff_value.errors:
            response['errors'].append(error)
    return JsonResponse(response)