# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from requests_tracker.models import Config


@never_cache
def index(request):
    value = Config.objects.get(key="is_track").value
    cache.set("is_track", value)
    return render(request, "index.html")
