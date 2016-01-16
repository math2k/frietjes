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
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^order$', OrderFormView.as_view(), name="order"),
    url(r'^order/(?P<order>.+)$', OrderView.as_view(), name="order-view"),
    url(r'^toggle-paid-flag/(?P<uo>.+)$', TogglePaidFlag.as_view(), name="toggle-paid-flag"),
    url(r'^pick-random/(?P<o>.+)$', PickRandomDeliveryPerson.as_view(), name="pick-random")
]
