# -*- coding: utf-8 -*-

from django.http import JsonResponse


__author__ = 'D.Ivanets'


def check(request):
    return JsonResponse({'is_active': True})