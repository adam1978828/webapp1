# -*- coding: utf-8 -*-
from functools import wraps
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404

__author__ = 'D.Ivanets'


def access_focus(func):
    def inner_decorator(request, *args, **kwargs):
        if request.user.is_focus:
            return func(request, *args, **kwargs)
        else:
            raise Http404
    return inner_decorator


def access_company(func):
    def inner_decorator(request, *args, **kwargs):
        if request.user.is_company:
            return func(request, *args, **kwargs)
        else:
            raise Http404
    return inner_decorator


def permission_required(*sys_funcs):
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return redirect_to_login(request.path)

            for sys_func in sys_funcs:
                if sys_func not in request.user.rights:
                    raise PermissionDenied
            return func(request, *args, **kwargs)
        return wraps(func)(inner_decorator)
    return decorator


def client_site(func):
    def inner_decorator(request, *args, **kwargs):
        if request.company:
            return func(request, *args, **kwargs)
        else:
            raise Http404
    return inner_decorator


def company_site(func):
    def inner_decorator(request, *args, **kwargs):
        if not request.company:
            return func(request, *args, **kwargs)
        else:
            raise Http404
    return inner_decorator
