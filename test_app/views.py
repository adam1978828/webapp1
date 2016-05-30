import json
from pprint import pprint
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
# from Model import Timezone, Currency, NoInternetOperation, PreauthMethod


# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from Model import Deal
from Model import FeaturedMovie, Movie


def index(request):
    company = request.company
    featured = request.db_session.query(Movie).join(FeaturedMovie).filter_by(company_id=company.id).all()
    movies = request.db_session.query(Movie).limit(10)
    return render(request, 'test_index.html', locals())


def test(request, name):
    # tz = request.db_session.query(Timezone).all()
    # cs = request.db_session.query(Currency).all()
    # nop = request.db_session.query(NoInternetOperation).all()
    # pm = request.db_session.query(PreauthMethod).all()
    # return render_to_response('test/%s.html' % name, {'timezones': tz, 'currency': cs,
    #                                                   'preauth_method': pm, 'no_internet_operation': nop},
    #                           context_instance=RequestContext(request))
    deals = request.db_session.query(Deal).limit(5).all()
    upcs = request.db_session.query(Deal).limit(10).all()
    return render_to_response('test/%s.html' % name, {'deals': deals, 'upcs':upcs},
                              context_instance=RequestContext(request))


def json_resp(request, name):
    # tz = request.db_session.query(Timezone).all()
    # cs = request.db_session.query(Currency).all()
    # nop = request.db_session.query(NoInternetOperation).all()
    # pm = request.db_session.query(PreauthMethod).all()
    # return render_to_response('test/%s.html' % name, {'timezones': tz, 'currency': cs,
    #                                                   'preauth_method': pm, 'no_internet_operation': nop},
    #                           context_instance=RequestContext(request))
    return render_to_response('json/%s.json' % name,
                              context_instance=RequestContext(request))


@csrf_exempt
def print_request(request):
    pprint(json.loads(request.body))
    return HttpResponse()