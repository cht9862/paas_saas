# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from rest_framework import routers as drf_routers

from apps.backend import views
from apps.backend.plugin.views import PluginViewSet, export_download, upload_package
from apps.backend.subscription.views import SubscriptionViewSet

routers = drf_routers.DefaultRouter(trailing_slash=True)
routers.register("plugin", PluginViewSet, basename="plugin")
routers.register("subscription", SubscriptionViewSet, basename="subscription")

export_routers = drf_routers.DefaultRouter(trailing_slash=True)

urlpatterns = [
    url(r"api/", include(routers.urls)),
    url(r"^package/upload/$", upload_package),
    url(r"^export/download/$", export_download, name="export_download"),
    url(r"^export/", include(export_routers.urls)),
    url(r"^get_gse_config/", views.get_gse_config),
    url(r"^report_log/", views.report_log),
]
