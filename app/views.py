# -*- coding: utf-8 -*-
import csv
import datetime
import random
import uuid

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.forms import formset_factory, Select
from django.forms.models import modelformset_factory
from django.utils.decorators import method_decorator

from app.forms import OrderForm, UserOrderForm, UserOrder, NotificationRequestForm, ImportMenuItemsForm
from app.models import Order, MenuItem, UserOrderItem, NotificationRequest, MenuItemCategory
from django.views.generic import TemplateView, FormView, View, RedirectView, CreateView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from app.signals import *


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = {}
        if self.request.GET.get('all'):
            ctx['all_orders'] = Order.objects.all().order_by("-pk")
        else:
            ctx['all_orders'] = Order.objects.all().order_by("-pk")[:6]
        ctx['open_order'] = Order.objects.filter(open=True).order_by("-date").last()
        ctx['col_size'] = int(len(ctx['all_orders']) / 2)
        ctx['feed_entries'] = FeedEntry.objects.filter(datetime__day=datetime.datetime.now().day).order_by('-datetime')[:15]
        ctx['show_notification_tooltip'] = False if self.request.COOKIES.get('show_notification_tooltip') == '0' else True
        if self.request.user.is_authenticated():
            ctx['unpaid_orders'] = UserOrder.objects.filter(user=self.request.user, paid=False, order__open=False)
        return ctx


@method_decorator(login_required, name='dispatch')
class OrderFormView(FormView):
    template_name = "order.html"
    form_class = UserOrderForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        ctx = super(OrderFormView, self).get_context_data(**kwargs)
        ctx['order'] = get_object_or_404(Order, pk=self.kwargs['order'])
        order_form_formset = formset_factory(form=OrderForm, extra=10, min_num=1, validate_min=True)
        # qs = UserOrderItem.objects.filter(menu_item__category__provider__id=ctx['order'].provider.pk)
        if self.request.POST:
            ctx['order_form_formset'] = order_form_formset(self.request.POST,
                                                           form_kwargs={'provider': ctx['order'].provider})
            ctx['user_order'] = UserOrderForm(self.request.POST)
        else:
            ctx['order_form_formset'] = order_form_formset(form_kwargs={'provider': ctx['order'].provider})
            ctx['user_order'] = UserOrderForm(initial={'order': ctx['order'], 'name': self.request.user.username})
        return ctx

    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs.get('order'))
        order_form_formset = formset_factory(OrderForm, min_num=1, validate_min=True)
        of_formset_instance = order_form_formset(self.request.POST, form_kwargs={'provider': order.provider})
        if of_formset_instance.is_valid():
            form.instance.user = self.request.user
            form.instance.save()
            for f in of_formset_instance:
                if f.is_valid() and f.instance.menu_item_id is not None:
                    f.instance.user_order = form.instance
                    f.instance.save()
            fe = FeedEntry(event='_{0}_ placed an order at {1}'.format(self.request.user.username, order.provider.name))
            fe.save()
            messages.success(self.request, "Your order has been saved!")
        else:
            form.add_error(None, "You need to select something!")
            return super(OrderFormView, self).form_invalid(form)
        return super(OrderFormView, self).form_valid(form)

    def form_invalid(self, form):
        return super(OrderFormView, self).form_invalid(form)


class TogglePaidFlag(View):
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            uo = get_object_or_404(UserOrder, pk=kwargs.get('uo'))
            uo.paid = not uo.paid
            uo.save()
            messages.success(request, "{0}'s order marked as {1}".format(uo.user.username, "paid" if uo.paid else "not paid"))
            if uo.paid:
                fe = FeedEntry(event='_{0}_ paid their order'.format(uo.user.username))
                fe.save()
            return redirect(request.META.get('HTTP_REFERER'))


class Redirect(RedirectView):
    pattern_name = "home"

    def get_redirect_url(self, *args, **kwargs):
        messages.success(self.request,
                         "Check this out! We have moved to a more appropriate .eu domain: 4lunch.eu, woohoo!")
        return super(Redirect, self).get_redirect_url(*args, **kwargs)


class PickRandomDeliveryPerson(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            o = get_object_or_404(Order, pk=kwargs.get('o'))
            if o.delivery_person:
                messages.error(request, "{0} is already set as the chinese volunteer!".format(o.delivery_person.username))
            else:
                o.assign_random_delivery_person()
                if o.delivery_person:
                    messages.success(request, "{0} has been selected as chinese volunteer! Thanks {0} :D".format(
                        o.delivery_person.username))
                    fe = FeedEntry(event='_{0}_ has been randomly selected to pick up the order from {1}'
                                   .format(o.delivery_person.username, o.provider.name))
                    fe.save()
                else:
                    messages.error(request, "Something went wrong .. do you have orders ?")
        return redirect(request.META.get('HTTP_REFERER'))


class OrderView(TemplateView):
    template_name = "order-view.html"

    def get_context_data(self, **kwargs):
        ctx = super(OrderView, self).get_context_data(**kwargs)
        ctx['order'] = Order.objects.get(pk=kwargs['order'])
        ctx['order_items'] = UserOrderItem.objects.filter(user_order__order=ctx['order']). \
            values('menu_item__name').annotate(count=Count('menu_item__name')).order_by('menu_item__category__order')
        return ctx


@method_decorator(login_required, name='dispatch')
class NotificationRequestFormView(UpdateView):
    form_class = NotificationRequestForm
    model = NotificationRequest
    template_name = 'notificationrequest_form.html'

    def dispatch(self, request, *args, **kwargs):
        res = super(NotificationRequestFormView, self).dispatch(request, *args, **kwargs)
        res.set_cookie('show_notification_tooltip', '0', expires="Fri, 01-Jan-25 12:12:12 GMT")
        return res

    def get_object(self, queryset=None):
        obj, created = NotificationRequest.objects.get_or_create(user=self.request.user)
        return obj

    def form_valid(self, form):
        resp = super(NotificationRequestFormView, self).form_valid(form)
        return resp

    def get_success_url(self):
        if len(self.object.providers.all()) > 0 or self.object.all_providers or self.object.deliveries:
            messages.success(self.request, "Notifications saved!")
        else:
            messages.warning(self.request, "We won't bother you with notifications again")
        return reverse_lazy('home')


@method_decorator(login_required, name='dispatch')
class NotificationCancelFormView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            NotificationRequest.objects.get(secret=self.kwargs['s']).delete()
            messages.success(self.request, "You won't receive any email from us anymore!")
        except:
            messages.error(self.request, "Something went wrong :(")
        return reverse_lazy('home')


class ImportMenuItemsFormView(FormView):
    form_class = ImportMenuItemsForm
    template_name = "import.html"

    def get_context_data(self, **kwargs):
        ctx = super(ImportMenuItemsFormView, self).get_context_data(**kwargs)
        ctx['categories'] = MenuItemCategory.objects.all().select_related('provider')
        return ctx

    def form_valid(self, form):
        csv_content = form.cleaned_data['csv']
        reader = csv.reader(csv_content.splitlines(), delimiter=";")
        for row in reader:
            mi = MenuItem(name=unicode(row[0]), unit_price=row[1], category_id=row[2])
            mi.save()
            messages.success(self.request, u"Saved {name} at {price}€".format(name=row[0], price=row[1]))

        return super(ImportMenuItemsFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home')