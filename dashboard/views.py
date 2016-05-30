from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Model import DiskOut30DaysView, Income30DaysView
from django.core.exceptions import PermissionDenied


__author__ = 'D.Kalpakchi'


@login_required
def all_charts(request):
    if request.user.is_company:
        disks_out = request.db_session.query(DiskOut30DaysView)\
                .filter_by(company_id=request.user.company.id)\
                .all()
        incomes = request.db_session.query(Income30DaysView)\
                .filter_by(company_id=request.user.company.id)\
                .all()
    else:
        raise PermissionDenied
    return render(request, 'dashboard_index.html', {'disks_out': disks_out, 'incomes': incomes})


