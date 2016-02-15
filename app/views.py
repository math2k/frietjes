import datetime
import random
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.forms import formset_factory, Select
from django.forms.models import modelformset_factory
from app.forms import OrderForm, UserOrderForm, UserOrder, NotificationRequestForm
from app.models import Order, MenuItem, UserOrderItem, NotificationRequest
from django.views.generic import TemplateView, FormView, View, RedirectView, CreateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages


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
        ctx['heading'] = random.choice((
            'A day without fritjes is a day wasted',
            'A fritje a day, keeps the doctor away'
        ))
        ctx['show_notification_tooltip'] = False if self.request.COOKIES.get('show_notification_tooltip') == '0' else True
        return ctx


class OrderFormView(FormView):
    template_name = "order.html"
    form_class = UserOrderForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        ctx = super(OrderFormView, self).get_context_data(**kwargs)
        ctx['order'] = get_object_or_404(Order, pk=self.kwargs['order'])
        order_form_formset = formset_factory(form=OrderForm, extra=10, min_num=0)
        # qs = UserOrderItem.objects.filter(menu_item__category__provider__id=ctx['order'].provider.pk)
        if self.request.POST:
            ctx['order_form_formset'] = order_form_formset(self.request.POST,
                                                           form_kwargs={'provider': ctx['order'].provider})
            ctx['user_order'] = UserOrderForm(self.request.POST)
        else:
            ctx['order_form_formset'] = order_form_formset(form_kwargs={'provider': ctx['order'].provider})
            ctx['user_order'] = UserOrderForm(initial={'order': ctx['order']})
        return ctx

    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs.get('order'))
        form.instance.save()
        order_form_formset = formset_factory(OrderForm)
        for f in order_form_formset(self.request.POST, form_kwargs={'provider': order.provider}):
            if f.is_valid() and f.instance.menu_item_id is not None:
                f.instance.user_order = form.instance
                f.instance.save()
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
            messages.success(request, "{0}'s order marked as {1}".format(uo.name, "paid" if uo.paid else "not paid"))
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
                messages.error(request, "{0} is already set as the chinese volunteer!".format(uo.delivery_person.name))
            else:
                o.assign_random_delivery_person()
                if o.delivery_person:
                    messages.success(request, "{0} has been selected as chinese volunteer! Thanks {0} :D".format(
                        o.delivery_person.name))
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


class NotificationRequestFormView(CreateView):
    form_class = NotificationRequestForm
    model = NotificationRequest
    template_name = 'notificationrequest_form.html'

    def dispatch(self, request, *args, **kwargs):
        res = super(NotificationRequestFormView, self).dispatch(request, *args, **kwargs)
        res.set_cookie('show_notification_tooltip', '0', expires="Fri, 01-Jan-25 12:12:12 GMT")
        return res

    def get_success_url(self):
        messages.success(self.request, "We'll send you a notification as soon as you can place an order!")
        return reverse_lazy('home')


class NotificationCancelFormView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            NotificationRequest.objects.get(secret=self.kwargs['s']).delete()
            messages.success(self.request, "You won't receive any email from us anymore!")
        except:
            messages.error(self.request, "Something went wrong :(")
        return reverse_lazy('home')
