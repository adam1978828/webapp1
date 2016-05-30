# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

__author__ = 'D.Ivanets'


@login_required()
def error404(request):
    return render_to_response('acc_404.html',
                              context_instance=RequestContext(request))


@login_required()
def error403(request):
    return render_to_response('acc_403.html',
                              context_instance=RequestContext(request))
