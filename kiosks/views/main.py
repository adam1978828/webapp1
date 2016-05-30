# -*- coding: utf-8 -*-
from json import loads

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from Model import Kiosk
from acc.decorators import permission_required


@login_required(login_url='/auth/login')
@permission_required('kiosk_view')
def view_list(request):
    query = request.db_session.query(Kiosk)
    if request.user.is_company:
        query = query.filter(Kiosk.company_id == request.user.company_id)
    kiosks = query.all()
    return render(request, 'kiosk_list.html', {'kiosks': kiosks})