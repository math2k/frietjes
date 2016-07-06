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
from django.conf.urls.static import static

from app.views import *
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/register/(?P<secret>.{32})$', FrietjesRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^redirect', Redirect.as_view(), name="redirect"),
    url(r'^user-order/(?P<user_order>.+)/view$', UserOrderView.as_view(), name="user-order-view"),
    url(r'^user-order/(?P<pk>.+)/delete', UserOrderDeleteView.as_view(), name="user-order-delete"),
    url(r'^order/(?P<order>.+)/view$', OrderView.as_view(), name="order-view"),
    url(r'^group/(?P<group>.+)/view$', JoinGroupFormView.as_view(), name="group-view"),
    url(r'^group/(?P<pk>.+)/leave', LeaveGroupView.as_view(), name="group-leave"),
    url(r'^group/(?P<pk>.+)/leave', LeaveGroupView.as_view(), name="group-leave"),
    url(r'^order/(?P<pk>.+)/update', UpdateOrderFormView.as_view(), name="order-update"),
    url(r'^group/(?P<pk>.+)/update', UpdateGroupFormView.as_view(), name="group-update"),
    url(r'^user-order/(?P<order>.+)/new$', CreateUserOrderFormView.as_view(), name="order"),
    url(r'^toggle-paid-flag/(?P<uo>.+)$', TogglePaidFlag.as_view(), name="toggle-paid-flag"),
    url(r'^toggle-user-staff-flag/(?P<pk>.+)$', ToggleUserStaffFlag.as_view(), name="toggle-user-staff-flag"),
    url(r'^set-order-delivered/(?P<pk>.+)$', SetOrderDeliveredView.as_view(), name="set-order-delivered"),
    url(r'^pick-random/(?P<o>.+)$', PickRandomDeliveryPerson.as_view(), name="pick-random"),
    url(r'^notifications', NotificationRequestFormView.as_view(), name="notifications"),
    url(r'^notification/cancel/(?P<s>.{32})', NotificationCancelFormView.as_view(), name="notification-cancel"),
    url(r'^import', ImportMenuItemsFormView.as_view(), name="import"),
    url(r'^invite', UserInviteFormView.as_view(), name="invite-form"),
    url(r'^order/new', CreateOrderFormView.as_view(), name="order-new"),
    url(r'^group/new', CreateGroupFormView.as_view(), name="group-new"),
    url(r'^place/(?P<pk>.+)', FoodProviderQuickView.as_view(), name="place-view"),
    url(r'^user-orders/(?P<pk>.+)', ListUserOrdersView.as_view(), name="user-order-list"),
    url(r'^user/(?P<pk>.+)/delete', DeleteUser.as_view(), name="user-delete"),
    url(r'^users', ListCompanyUsers.as_view(), name="user-list"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf.urls import include, patterns, url

if settings.DEBUG:
    import debug_toolbar
#    urlpatterns += patterns('',
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    )
