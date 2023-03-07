"""mospweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("info/", include("info.urls")),
    path("markdownx/", include("markdownx.urls")),
    path("", include("core.urls")),
    path(
        "static/<path:f>",
        RedirectView.as_view(url=(settings.STATIC_URL or "") + "%(f)s"),
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(url="https://web.evanchen.cc/favicon.ico"),
    ),
]
if settings.DEBUG is True or settings.STATIC_URL is None:
    urlpatterns.pop()

if settings.DEBUG:
    admin.site.site_header = "127.0.0.1"
    admin.site.index_title = "Switchboard"
    admin.site.site_title = "mosp@localhost"
else:
    admin.site.site_header = "MOSP Headquarters"
    admin.site.index_title = "GM Panel"
    admin.site.site_title = "MOSP HQ"
