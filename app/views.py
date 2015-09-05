from app.models import Order
from django.shortcuts import render
from django.views.generic import TemplateView, FormView


class HomeView(TemplateView):
    template_name = "home.html"


    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['all_orders'] = Order.objects.all().order_by("-date")

        return ctx

class OrderView(FormView):
    template_name = "order.html"

    def get_context_data(self, **kwargs):
        ctx = {}
        return ctx
