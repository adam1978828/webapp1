from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response  # render
from django.contrib.auth.decorators import login_required
from Model import Address, User, Company, Kiosk


@login_required(login_url='/auth/login/')
def staff_list(request):
    if request.user.is_focus:
        staff = request.db_session.query(User).filter_by(user_type_id=3).all()
    elif request.user.is_company:
        staff = request.db_session.query(User).filter_by(user_type_id=2)\
            .filter_by(company_id=request.user.company_id).all()
    else:
        raise Http404
    return render_to_response('staff_list.html', {'staff': staff},
                              context_instance=RequestContext(request))


@login_required()
def error404(request):
    return render_to_response('acc_404.html', {'message': ''},
                              context_instance=RequestContext(request))
