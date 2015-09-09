import datetime
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.forms import formset_factory, Select
from app.forms import OrderForm, UserOrderForm
from app.models import Order, MenuItem, UserOrderItem
from django.views.generic import TemplateView, FormView


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['all_orders'] = Order.objects.all().order_by("-date")
        ctx['open_order'] = Order.objects.filter(open=True).order_by("-date").last()
        return ctx


class OrderFormView(FormView):
    template_name = "order.html"
    form_class = UserOrderForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        ctx = super(OrderFormView, self).get_context_data(**kwargs)
        ctx['order'] = Order.objects.filter(open=True).order_by("-date").first()
        order_form_formset = formset_factory(OrderForm, extra=10, min_num=0)
        if self.request.POST:
            ctx['order_form_formset'] = order_form_formset(self.request.POST)
            ctx['user_order'] = UserOrderForm(self.request.POST)
        else:
            ctx['order_form_formset'] = order_form_formset()
            ctx['user_order'] = UserOrderForm(initial={'order': ctx['order']})
        return ctx

    def form_valid(self, form):
        form.instance.save()
        order_form_formset = formset_factory(OrderForm)
        for f in order_form_formset(self.request.POST):
            if f.is_valid() and f.instance.menu_item_id is not None:
                f.instance.user_order = form.instance
                f.instance.save()
        return super(OrderFormView, self).form_valid(form)

    def form_invalid(self, form):
        return super(OrderFormView, self).form_invalid(form)


class OrderView(TemplateView):
    template_name = "order-view.html"

    def get_context_data(self, **kwargs):
        ctx = super(OrderView, self).get_context_data(**kwargs)
        ctx['order'] = Order.objects.get(pk=kwargs['order'])
        ctx['order_items'] = UserOrderItem.objects.filter(user_order__order=ctx['order']).\
            values('menu_item__name').annotate(count=Count('menu_item__name')).order_by('menu_item__category__order')
        return ctx