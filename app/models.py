# -*- coding: utf-8 -*-
import uuid

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.utils.functional import cached_property


class UserOrder(models.Model):
    user = models.ForeignKey(User)
    order = models.ForeignKey('Order')
    paid = models.BooleanField(default=False)
    notes = models.TextField(default="", blank=True)

    @cached_property
    def total(self):
        total = self.userorderitem_set.all().aggregate(sum=models.Sum('menu_item__unit_price'))['sum']
        return total

    def __unicode__(self):
        return u"{0} - {1}".format(self.user.username, self.order.date, self.paid)


class MenuImage(models.Model):
    image = models.ImageField(upload_to='menus')
    provider = models.ForeignKey('FoodProvider')


class FoodProvider(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=300)

    def __unicode__(self):
        return u"{0}".format(self.name)


class Order(models.Model):
    open = models.BooleanField(default=True, verbose_name="Open for ordering")
    delivered = models.BooleanField(default=False)
    manager = models.ForeignKey(User)
    provider = models.ForeignKey(FoodProvider, verbose_name="Place", related_name='provider')
    date = models.DateField(auto_now_add=True)
    delivery_person = models.ForeignKey(User, blank=True, null=True, related_name="delivery_person")
    delivery_time = models.TimeField(blank=True, null=True)
    closing_time = models.TimeField(blank=True, null=True)
    notes = models.TextField(default="", blank=True)
    silent = models.BooleanField(default=False, help_text="Don't send notifications for this order")

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self._original_open = self.open
        self._original_delivered = self.delivered

    def get_userorders(self):
        return self.userorder_set.all().prefetch_related('userorderitem_set__menu_item')

    @cached_property
    def total(self):
        total = 0
        for uo in self.userorder_set.all().prefetch_related('userorderitem_set__menu_item'):
            for uoi in uo.userorderitem_set.all():
                total += uoi.menu_item.unit_price
        return total

    def assign_random_delivery_person(self):
        self.delivery_person = self.userorder_set.order_by('?').first().user
        self.save()

    @property
    def has_unpaid_user_order(self):
        return len(UserOrder.objects.filter(order=self.pk, paid=False)) > 0

    def save(self, **kwargs):
        if self._original_open != self.open and not self.open:
            fe = FeedEntry(event='Order at _{0}_ has been closed'.format(self.provider.name))
            fe.save()
        if self._original_delivered != self.delivered and self.delivered:
            fe = FeedEntry(event='Order at _{0}_ has been delivered!<br/> Woohoo!'.format(self.provider.name))
            fe.save()
            if self.silent:
                return super(Order, self).save(**kwargs)
            users = set([uo.user for uo in self.userorder_set.filter()])
            nrs = NotificationRequest.objects.filter(deliveries=True, user__in=users)
            for nr in nrs:
                body = """
Hey {name},

The order from {place} has been delivered!

Cheers,
--
4lunch.eu

To cancel notifications, visit this address: http://whats.4lunch.eu{cancel_url}
        """.format(name=nr.user.username, place=self.provider.name, cancel_url=reverse_lazy('notifications'))
                send_mail("What's for lunch? - 4lunch.eu", body, '4lunch.eu notifications <notifications@4lunch.eu>',
                    [nr.user.email], fail_silently=True)

        return super(Order, self).save(**kwargs)

    def __unicode__(self):
        return self.date.strftime("%d-%m-%y")


class UserOrderItem(models.Model):
    user_order = models.ForeignKey(UserOrder)
    menu_item = models.ForeignKey("MenuItem")

    @property
    def total(self):
        return self.menu_item.unit_price

    def __unicode__(self):
        return u"{0}".format(self.menu_item.name)


class MenuItemCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField()
    provider = models.ForeignKey(FoodProvider)

    def __unicode__(self):
        return u"{0}".format(self.name)


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(MenuItemCategory)

    @property
    def provider(self):
        return self.category.provider

    def __unicode__(self):
        return u"{0} - {1}€".format(self.name, self.unit_price)


class NotificationRequest(models.Model):
    user = models.ForeignKey(User)
    providers = models.ManyToManyField(to=FoodProvider, blank=True)
    secret = models.CharField(max_length=32, null=True, blank=True)
    all_providers = models.BooleanField(default=False)
    deliveries = models.BooleanField(default=False)

    @property
    def selected_providers(self):
        return ', '.join([p.name for p in self.providers.all()])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.secret = str(uuid.uuid4())[:32]
        return super(NotificationRequest, self).save(*args, **kwargs)

    def __repr__(self):
        return self.user.email

    def __unicode__(self):
        return self.user.email


class FeedEntry(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    event = models.TextField()
