# -*- coding: utf-8 -*-
from django.shortcuts import render


def error_404(request):
    """
    404提示页
    """
    return render(request, '404.html')


def error_500(request):
    """
    500提示页
    """
    return render(request, '500.html')


def error_401(request):
    """
    401提示页
    """
    return render(request, '401.html')


def error_403(request):
    """
    403提示页
    """
    return render(request, '403.html')
