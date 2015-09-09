# -*- coding: utf-8 -*-
from django.db import models


class Order(models.Model):
    manager = models.CharField(max_length=50)
    open = models.BooleanField(default=True)
    notes = models.TextField(default="", blank=True)
    date = models.DateField(auto_now=True)

    @property
    def total(self):
        total = 0
        for uo in self.userorder_set.all():
            for uoi in uo.userorderitem_set.all():
                total += uoi.menu_item.unit_price
        return total

    def __unicode__(self):
        return self.date.strftime("%d-%m-%y")


class UserOrder(models.Model):
    name = models.CharField(max_length=50)
    order = models.ForeignKey(Order)
    paid = models.BooleanField(default=False)
    notes = models.TextField(default="", blank=True)

    @property
    def total(self):
        total = 0
        for uo in self.userorderitem_set.all():
            total += uo.menu_item.unit_price
        return total

    def __unicode__(self):
        return "{0} - {1}".format(self.name, self.order.date, self.paid)


class UserOrderItem(models.Model):
    user_order = models.ForeignKey(UserOrder)
    menu_item = models.ForeignKey("MenuItem")

    @property
    def total(self):
        return self.menu_item.unit_price

    def __unicode__(self):
        return "{0}".format(self.menu_item.name)


class MenuItemCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField()

    def __unicode__(self):
        return u"{0}".format(self.name)


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(MenuItemCategory)

    def __unicode__(self):
        return u"{0} - {1}€".format(self.name, self.unit_price)


