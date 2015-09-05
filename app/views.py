from app.forms import OrderForm
from app.models import Order
from django.views.generic import TemplateView, FormView


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['all_orders'] = Order.objects.all().order_by("-date")

        return ctx


class OrderView(FormView):
    template_name = "order.html"
    form_class = OrderForm

    def get_context_data(self, **kwargs):
        ctx = super(OrderView, self).get_context_data(**kwargs)
        ctx['order'] = Order.objects.filter(open=True).order_by("-date").first()
        return ctx
