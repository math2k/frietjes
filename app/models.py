from django.db import models


class Order(models.Model):
    date = models.DateField()
    notes = models.TextField(default="")
    manager = models.CharField(max_length=50)
    open = models.BooleanField(default=True)

    @property
    def total(self):
        total = 0
        for uo in self.userorder_set.all():
            for uoi in uo.userorderitem_set.all():
                total += uoi.menu_item.unit_price * uoi.quantity
        return total

    def __unicode__(self):
        return self.date.strftime("%d-%m-%y")


class UserOrder(models.Model):
    name = models.CharField(max_length=50)
    order = models.ForeignKey(Order)

    def __unicode__(self):
        return self.name


class UserOrderItem(models.Model):
    user_order = models.ForeignKey(UserOrder)
    menu_item = models.ForeignKey("MenuItem")
    quantity = models.IntegerField()

    def __unicode__(self):
        return "{0} x {1}".format(self.menu_item.name, self.quantity)


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __unicode__(self):
        return self.name


