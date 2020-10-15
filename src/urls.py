# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from version_log import config

urlpatterns = [
    url(r'^admin_nodeman/', admin.site.urls),
    url(r'^account/', include('blueapps.account.urls')),

    url(r'^backend/', include('apps.backend.urls')),
    url(r'^', include('apps.node_man.urls')),

    url(r'^{}'.format(config.ENTRANCE_URL), include('version_log.urls')),
]

# handler404 = 'common.error_views.error_404'
# handler500 = 'common.error_views.error_500'
# handler403 = 'common.error_views.error_403'
# handler401 = 'common.error_views.error_401'
