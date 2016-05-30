# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse

from Model import Kiosk
from Model import KioskKioskManager, CompanyKioskManager

from libs.validators.core import json_response_content
from acc.decorators import permission_required
from sqlalchemy import or_, and_


@login_required
@permission_required('company_view_permissions')
def permissions(request, kiosk_id):
    from Model import User
    from sqlalchemy.sql import union, select
    kiosk = request.db_session.query(Kiosk).filter_by(id=kiosk_id).first()
    ckmt = CompanyKioskManager.__table__
    kkmt = KioskKioskManager.__table__
    company_granted = select(
        [ckmt.c.company_id.label('company'),
         ckmt.c.user_id.label('user_id'),
         kkmt.c.kiosk_id.label('kiosk')],
        from_obj=ckmt.outerjoin(kkmt, ckmt.c.user_id == kkmt.c.user_id)).\
        where(or_(kkmt.c.kiosk_id == kiosk_id, None == kkmt.c.kiosk_id))
    kiosk_granted = select(
        [ckmt.c.company_id.label('company'),
         kkmt.c.user_id.label('user_id'),
         kkmt.c.kiosk_id.label('kiosk')],
        from_obj=kkmt.outerjoin(ckmt, kkmt.c.user_id == ckmt.c.user_id)).\
        where(or_(kkmt.c.kiosk_id == kiosk_id, None == kkmt.c.kiosk_id))
    granted = union(company_granted, kiosk_granted).alias('granted')
    kiosk_granted = request.db_session.query(User)\
        .join(kiosk_granted.alias('kg'), User.id == kiosk_granted.c.user_id).all()
    granted_users = request.db_session.query(granted, User).join(User, granted.c.user_id == User.id).all()
    return render(request, 'kiosk_permissions.html',
                  {'users': [u for u in kiosk.company.users if u not in kiosk_granted],
                   'granted': granted_users,
                   'kioskId': kiosk_id})


@login_required
@require_POST
def add_permission(request, kiosk_id):
    from decimal import Decimal
    user_id = request.POST.get('userId', None)
    if user_id:
        granted_user = KioskKioskManager(kiosk_id, user_id)
        request.db_session.add(granted_user)
        request.db_session.commit()
        response = json_response_content('success', 'Permissions granted successfully')
        response['data'] = {
            'granted_full_name': granted_user.user.full_name
        }
        # return JsonResponse(response)
        return HttpResponseRedirect(reverse('kiosks.views.permissions', args=(Decimal(kiosk_id),)))
    else:
        return JsonResponse(json_response_content('error', 'User field is required'))


@login_required
@require_POST
def remove_permission(request, kiosk_id, user_id):
    from decimal import Decimal
    granted_user = request.db_session.query(KioskKioskManager).\
        filter_by(kiosk_id=kiosk_id, user_id=user_id).first()
    request.db_session.delete(granted_user)
    request.db_session.commit()
    response = json_response_content('success', 'Kiosk permission removed successfully')
    response['redirect_url'] = reverse('kiosks.views.permissions', args=(Decimal(kiosk_id),))
    return JsonResponse(response)