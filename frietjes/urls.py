"""fritjes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from app.views import *
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/$', FrietjesRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^redirect', Redirect.as_view(), name="redirect"),
    url(r'^order/(?P<order>.+)/view$', OrderView.as_view(), name="order-view"),
    url(r'^order/(?P<order>.+)$', NewOrderFormView.as_view(), name="order"),
    url(r'^toggle-paid-flag/(?P<uo>.+)$', TogglePaidFlag.as_view(), name="toggle-paid-flag"),
    url(r'^pick-random/(?P<o>.+)$', PickRandomDeliveryPerson.as_view(), name="pick-random"),
    url(r'^notifications', NotificationRequestFormView.as_view(), name="notifications"),
    url(r'^notification/cancel/(?P<s>.{32})', NotificationCancelFormView.as_view(), name="notification-cancel"),
    url(r'^import', ImportMenuItemsFormView.as_view(), name="import"),
]

from django.conf import settings
from django.conf.urls import include, patterns, url

if settings.DEBUG:
    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )
