# -*- coding: utf-8 -*-
from django.db import models
from django.utils.functional import cached_property

class UserOrder(models.Model):
    name = models.CharField(max_length=50)
    order = models.ForeignKey('Order')
    paid = models.BooleanField(default=False)
    notes = models.TextField(default="", blank=True)

    @cached_property
    def total(self):
        total = 0
        total = self.userorderitem_set.all().aggregate(sum=models.Sum('menu_item__unit_price'))['sum']
        return total

    def __unicode__(self):
        return u"{0} - {1}".format(self.name, self.order.date, self.paid)


class FoodProvider(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=300)

    def __unicode__(self):
        return u"{0}".format(self.name)


class Order(models.Model):
    manager = models.CharField(max_length=50)
    provider = models.ForeignKey(FoodProvider, related_name='provider')
    open = models.BooleanField(default=True)
    notes = models.TextField(default="", blank=True)
    date = models.DateField(auto_now_add=True)
    delivery_person = models.ForeignKey('UserOrder', blank=True, null=True, related_name="delivery_person")

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
        self.delivery_person = self.userorder_set.order_by('?').first()
        self.save()

    @property
    def has_unpaid_user_order(self):
	return len(UserOrder.objects.filter(order=self.pk, paid=False)) > 0

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


