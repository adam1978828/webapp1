import time
import datetime


from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from sqlalchemy import or_
from sqlalchemy.orm.session import make_transient

from acc.decorators import permission_required
from libs.validators.core import json_response_content, validation_error
from datatables import ColumnDT, DataTables
from Model import Coupon, CouponType, Company, CouponView

import helpers.utils
import pickle

COUPON_COMP_FIELDS = ['company_id', 'coupon_type_id', 'params', 'usage_amount', 'code', 'per_card_usage', 'dt_start', 'dt_end']


@permission_required('coupons_view')
def all_coupons(request):
    """Displays all coupons for this company
    """
    if request.user.is_focus:
        companies = request.db_session.query(Company).all()
    patterns = request.db_session.query(CouponType).all()

    return render(request, 'coupons_all.html', locals())


def _unknown_column_value(val):
    return val if val is not None else '--'


def _empty_value(val):
    return ''


def _control_buttons(val, is_deleted):
    controls = '<a class="button small grey tooltip editcoupon" data-gravity="s" href="{0}"><i class="icon-pencil"></i></a>'.\
        format(reverse('coupons.views.edit_coupon_by_id', args=(val,)))

    controls += '<a class="button small grey tooltip restorecoupon {0}" data-gravity="s" href="{1}"><i class="icon-refresh"></i></a>'.\
        format('hidden' if not is_deleted else '', reverse('coupons.views.restore', args=(val,)))

    controls += '<a class="button small grey tooltip removecoupon {0}" data-gravity="s" href="{1}"><i class="icon-remove"></i></a>'.\
        format('hidden' if is_deleted else '', reverse('coupons.views.remove', args=(val,)))

    return controls


def _removed_indicator(val):
    return '<span class="badge block red">Yes</span>' if val else '<span class="badge block green">No</span>'


def _date_column(val):
    return val.strftime("%m/%d/%y") if val else '-'


@login_required
def json_all(request):
    columns = list()
    columns.append(ColumnDT('id'))
    columns.append(ColumnDT('coupon_type', filter=_unknown_column_value))
    columns.append(ColumnDT('coupon_code', filter=_unknown_column_value))
    columns.append(ColumnDT('coupon_pattern', filter=_unknown_column_value))
    columns.append(ColumnDT('usage_amount', filter=_unknown_column_value))
    columns.append(ColumnDT('per_card_usage', filter=_unknown_column_value))
    columns.append(ColumnDT('dt_start', filter=_date_column))
    columns.append(ColumnDT('dt_end', filter=_date_column))
    columns.append(ColumnDT('is_deleted', filter=_removed_indicator))
    if request.user.is_focus:
        columns.append(ColumnDT('company_name', filter=_unknown_column_value))

    if 'coupons_edit' in request.user.rights:
        columns.append(ColumnDT('id', filter=_control_buttons, custom_col_name='is_deleted'))
    else:
        columns.append(ColumnDT('id', filter=_empty_value))

    query = request.db_session.query(CouponView)

    if request.user.is_company:
        query = query.filter_by(company_id=request.user.company_id)

    table = DataTables(request, CouponView, query, columns)
    response = table.output_result()
    return JsonResponse(response)


def all_types(request):
    return render(request, 'coupons_all_types.html', {})


@require_POST
@permission_required('coupons_edit')
def add(request, coupon_id=None):
    if request.user.is_focus:
        company_id = int(request.POST.get('f_company_id', 1))
    else:
        company_id = request.user.company_id

    if coupon_id is not None:
        tmp_coup = request.db_session.query(Coupon).filter_by(id=coupon_id).first()
        if tmp_coup.is_deleted:
            response = json_response_content('success', 'Coupon is deleted! Modification is not allowed!')
            return JsonResponse(response)

    pattern_id = request.POST.get('couponTypeId', None)
    pattern_id = int(pattern_id)
    # think of how to fix this issue with []
    # NOTE: here those None values are handled in the appropriate validator in coupon
    params = request.POST.getlist('params[]', None) or request.POST.get('params', None)
    usage_amount, code = request.POST.get('usageAmount', None), request.POST.get('code', None)
    dt_start, dt_end = request.POST.get('dtStart', None), request.POST.get('dtEnd', None)
    per_card_usage = request.POST.get('perCardUsage', None)

    usage_amount = int(usage_amount) if usage_amount.isdigit() else usage_amount
    per_card_usage = int(per_card_usage) if per_card_usage.isdigit() else per_card_usage
    new_coupon = Coupon(company_id, pattern_id, params, usage_amount, code, per_card_usage)
    if params:
        try:
            value = params
            print 'params', params
            coupon_t = request.db_session.query(CouponType).filter_by(id=pattern_id).first()
            if isinstance(value, list):
                for item in value:
                    item = float(item)
            else:
                value = float(value)
            if pattern_id == 4:
                value[0] = value[0] + value[1]
                new_coupon.params = value
            dmp = pickle.dumps(value)
            params = pickle.loads(dmp)
            if coupon_t:
                if isinstance(params, tuple) or isinstance(params, list):
                    r = coupon_t.decoded_pattern.format(*params)
                else:
                    r = coupon_t.decoded_pattern.format(params)
        except Exception, e:
            no_params_error = True
            for err in new_coupon.errors:
                if err['field'] == 'params':
                    no_params_error = False
            if no_params_error:
                new_coupon.errors.append({'field': 'params', 'message': str(e)})

    if dt_start:
        dt_start = time.strptime(dt_start, "%d.%m.%Y")
        new_coupon.dt_start = datetime.datetime.fromtimestamp(time.mktime(dt_start))
    if dt_end:
        dt_end = time.strptime(dt_end, "%d.%m.%Y")
        new_coupon.dt_end = datetime.datetime.fromtimestamp(time.mktime(dt_end))
    if coupon_id is not None:
        coupon_id = int(coupon_id)
        current_coupon = request.db_session.query(Coupon).filter_by(id=coupon_id).first()
        main_coupon_id = current_coupon.main_coupon_id or coupon_id
        # if main_coupon_id is not None and current_coupon.modified_by_id is not None:
        if current_coupon.modified_by_id is not None:
            current_coupon = request.db_session.query(Coupon).filter_by(main_coupon_id=main_coupon_id).filter(Coupon.modified_by_id.is_(None)).first()

        if helpers.utils.is_same_objects(current_coupon, new_coupon, COUPON_COMP_FIELDS):
            response = json_response_content('success', 'Coupon did not change.')
            return JsonResponse(response)
        # deactivate current_coupon
        current_coupon.modified_by_id = request.user.id
        current_coupon.deactivate()
        # activate new coupon
        main_coupon_id = current_coupon.main_coupon_id or current_coupon.id
        new_coupon.main_coupon_id = main_coupon_id

    coupon_with_code = request.db_session.query(Coupon) \
        .filter(Coupon.is_deleted.isnot(True)) \
        .filter(Coupon.code.ilike('{}'.format(code))) \
        .filter_by(company_id=company_id)

    if coupon_id:
        coupon_id = int(coupon_id)
        coupon_with_code = coupon_with_code.filter(Coupon.id != coupon_id).first()
    else:
        coupon_with_code = coupon_with_code.first()

    if coupon_with_code:
        response = json_response_content('error', 'Invalid coupon code')
        response['errors'].append(validation_error('code', 'Such coupon code is already in use'))
    if new_coupon.no_errors():
        request.db_session.add(new_coupon)
        request.db_session.commit()
        if coupon_id is not None:
            response = json_response_content('success', 'Coupon was successfully changed')
        else:
            response = json_response_content('success', 'Coupon was successfully added')

        count = request.db_session.query(Coupon).filter(Coupon.is_deleted.isnot(True)).filter_by(company_id=company_id).count()
        response['redirect_url'] = reverse('coupons.views.edit_coupon_by_id', args=(new_coupon.id,))
    else:
        request.db_session.rollback()
        response = json_response_content('error', 'Invalid params values are given')
        for error in new_coupon.errors:
            if 'code' not in map(lambda x: x.get('field'), response['errors']):
                response['errors'].append(error)
    return JsonResponse(response)


# @login_required
@require_POST
@permission_required('coupons_edit')
def remove(request, coupon_id):
    if coupon_id:
        coupon_id = int(coupon_id)
        if request.user.is_focus:
            coupon = request.db_session.query(Coupon).filter_by(id=coupon_id, is_deleted=False).first()
        else:
            coupon = request.db_session.query(Coupon).filter_by(id=coupon_id, is_deleted=False, company_id=request.user.company_id).first()
        try:
            coupon.deactivate()
            coupon.modified_by_id = request.user.id
            request.db_session.commit()
            response = json_response_content('success', 'Coupon was successfully removed!')
        except Exception as e:
            request.db_session.rollback()
            response = json_response_content('error', 'There was an error during coupon remove: {0}'.format(str(e)))
        return JsonResponse(response)
    else:
        raise Http404


@require_POST
@permission_required('coupons_edit')
def restore(request, coupon_id):
    if coupon_id:
        coupon_id = int(coupon_id)
        if request.user.is_focus:
            coupon = request.db_session.query(Coupon).filter_by(id=coupon_id, is_deleted=True).first()
        else:
            coupon = request.db_session.query(Coupon).filter_by(id=coupon_id, is_deleted=True, company_id=request.user.company_id).first()
        try:
            coupon.modified_by_id = request.user.id
            request.db_session.commit()
            request.db_session.expunge(coupon)

            make_transient(coupon)
            coupon.main_coupon_id = coupon.main_coupon_id if coupon.main_coupon_id else coupon.id
            coupon.id = None
            coupon.restore()

            request.db_session.add(coupon)
            request.db_session.commit()
            response = json_response_content('success', 'Coupon was successfully restored!')
        except Exception as e:
            request.db_session.rollback()
            response = json_response_content('error', 'There was an error during coupon restore: {0}'.format(str(e)))
        return JsonResponse(response)
    else:
        raise Http404


@login_required
@permission_required('coupons_edit')
def edit_coupon_by_id(request, coupon_id):
    if coupon_id:
        coupon_id = int(coupon_id)
    data = dict()
    patterns = request.db_session.query(CouponType).all()
    data.update({'patterns': patterns})

    if coupon_id is None:
        raise Http404
    else:
        coupon_id = int(coupon_id)
        query = request.db_session.query(Coupon)
        coupon = query.filter_by(id=coupon_id)
        _coupon = coupon.first()
        main_coupon_id = _coupon.main_coupon_id or coupon_id
        if _coupon.modified_by_id is not None and not _coupon.is_deleted:
            coupon = query.filter_by(main_coupon_id=main_coupon_id).filter(Coupon.modified_by_id.is_(None))

    coupons = query.filter(or_(Coupon.main_coupon_id == main_coupon_id, Coupon.id == main_coupon_id)).all()
    data['coupons'] = coupons
    if request.user.is_focus:
        coupon = coupon.first()
        companies = request.db_session.query(Company).all()
        data.update({'coupon': coupon,
                     'companies': companies})
    elif request.user.is_company:
        coupon = coupon.filter(Coupon.company == request.user.company).first()
        data.update({'coupon': coupon})
    else:
        raise Http404
    return render(request, 'coupon_edit.html', data)