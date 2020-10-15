# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.urls import include
from django.conf import settings
from rest_framework import routers

from iam import IAM
from iam.contrib.django.dispatcher import DjangoBasicResourceApiDispatcher
from blueapps.account.decorators import login_exempt

from apps.node_man import views
from apps.node_man.iam_provider import BusinessResourceProvider, CloudResourceProvider, ApResourceProvider
from apps.node_man.views import ap, cloud, host, job, permission, meta, cmdb, tjj, choice, plugin, debug
from apps.node_man.views.plugin import GsePluginViewSet

iam = IAM(settings.APP_CODE, settings.SECRET_KEY, settings.BK_IAM_HOST, settings.BK_PAAS_INNER_HOST)

router = routers.DefaultRouter(trailing_slash=True)

router.register(r"ap", ap.ApViewSet, basename="ap")
router.register(r"cloud", cloud.CloudViewSet, basename="cloud")
router.register(r"host", host.HostViewSet, basename="host")
router.register(r"job", job.JobViewSet, basename="job")
router.register(r"permission", permission.PermissionViewSet, basename="permission")
router.register(r"cmdb", cmdb.CmdbViews, basename="cmdb")
router.register(r"debug", debug.DebugViews, basename="debug")
router.register(r"meta", meta.MetaViews, basename="meta")
router.register(r"tjj", tjj.TjjViews, basename="tjj")
router.register(r"choice", choice.ChoiceViewSet, basename="choice")
router.register(r"plugin/(?P<category>\w+)/process", GsePluginViewSet)
router.register(r"plugin", plugin.PluginViewSet, basename="plugin")
router.register(r"plugin/(?P<process>\w+)/package", plugin.PackagesViews, basename="package")
router.register(r"plugin/process", plugin.ProcessStatusViewSet, basename="process_status")
biz_dispatcher = DjangoBasicResourceApiDispatcher(iam, settings.BK_IAM_SYSTEM_ID)
biz_dispatcher.register("biz", BusinessResourceProvider())
cloud_dispatcher = DjangoBasicResourceApiDispatcher(iam, settings.BK_IAM_SYSTEM_ID)
cloud_dispatcher.register("cloud", CloudResourceProvider())
ap_dispatcher = DjangoBasicResourceApiDispatcher(iam, settings.BK_IAM_SYSTEM_ID)
ap_dispatcher.register("ap", ApResourceProvider())

urlpatterns = [
    url(r"^$", views.index),
    url(r"api/", include(router.urls)),
    url(r"api/iam/v1/biz", biz_dispatcher.as_view([login_exempt])),
    url(r"api/iam/v1/cloud", cloud_dispatcher.as_view([login_exempt])),
    url(r"api/iam/v1/ap", ap_dispatcher.as_view([login_exempt])),
]
