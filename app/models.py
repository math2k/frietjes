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
    phone = models.CharField(max_length=20, null=True)
    logo = models.ImageField(upload_to='logos', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    type = models.ManyToManyField(to='FoodProviderType')

    def __unicode__(self):
        return u"{0}".format(self.name)


class FoodProviderType(models.Model):
    name = models.CharField(primary_key=True, max_length=50, choices=(('takeaway', 'Takeaway'), ('restaurant', 'Restaurant'), ('shop', 'Shop')))

    def __unicode__(self):
        return u'{0}'.format(self.name)


class EatingGroup(models.Model):
    company = models.ForeignKey(to="Company")
    provider = models.ForeignKey(FoodProvider, verbose_name="Place")
    manager = models.ForeignKey(User)
    date = models.DateField(auto_now_add=True)
    open = models.BooleanField(default=True, verbose_name="Open for joining", help_text='')
    closing_time = models.DateTimeField(null=True, blank=True, help_text="Closing time for joining the outing")
    departing_time = models.DateTimeField(null=True, help_text="Time leaving the office")
    silent = models.BooleanField(default=False, help_text="Don't send notifications for this outing")
    notes = models.TextField(default="", blank=True)
    cancelled = models.BooleanField(default=False)
    cancelled_reason = models.TextField(null=True, blank=True, help_text="Reason for cancelling this outing")

    def __init__(self, *args, **kwargs):
        super(EatingGroup, self).__init__(*args, **kwargs)
        self._original_cancelled = self.cancelled

    def save(self, **kwargs):
        if self._original_cancelled != self.cancelled and self.cancelled:
            if self.silent:
                return super(EatingGroup, self).save(**kwargs)
            users = set([egm.user for egm in self.eatinggroupmember_set.all()])
            for u in users:
                body = """
Hey {name},

We are sorry to let you know that the order from {place} has been cancelled!

{reason}

Cheers,
--
4lunch.eu
                    """.format(name=u.username, place=self.provider.name,
                               reason='The reason given is: ' + self.cancelled_reason if self.cancelled_reason else 'No reason was given by the manager')
                send_mail("What's for lunch? - 4lunch.eu", body,
                          '4lunch.eu notifications <notifications@4lunch.eu>',
                          [u.email], fail_silently=True)

        return super(EatingGroup, self).save(**kwargs)

    def __unicode__(self):
        return u"{0} on {1}".format(self.provider.name, self.date)


class EatingGroupMember(models.Model):
    eating_group = models.ForeignKey(to=EatingGroup)
    user = models.ForeignKey(to=User)
    can_drive = models.BooleanField(default=False, help_text="I can drive and have a car.")
    notes = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u"{0} at {1} on {2}".format(self.user.username, self.eating_group.provider.name, self.eating_group.date)


class Order(models.Model):
    company = models.ForeignKey(to="Company")
    open = models.BooleanField(default=True, verbose_name="Open for ordering", help_text='')
    delivered = models.BooleanField(default=False)
    manager = models.ForeignKey(User)
    provider = models.ForeignKey(FoodProvider, verbose_name="Place", related_name='provider')
    date = models.DateField(auto_now_add=True)
    delivery_person = models.ForeignKey(User, blank=True, null=True, related_name="delivery_person", help_text='Can be picked at random as soon as users have placed an order')
    delivery_time = models.DateTimeField(null=True)
    closing_time = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(default="", blank=True)
    silent = models.BooleanField(default=False, help_text="Don't send notifications for this order")
    cancelled = models.BooleanField(default=False, help_text="Food won't be delivered for this order")
    cancelled_reason = models.TextField(null=True, blank=True, help_text="Reason for cancelling this order")

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self._original_open = self.open
        self._original_delivered = self.delivered
        self._original_cancelled = self.cancelled

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
        if self._original_cancelled != self.cancelled and self.cancelled:
                    fe = FeedEntry(event='Order at _{0}_ has been cancelled!'.format(self.provider.name))
                    fe.save()
                    if self.silent:
                        return super(Order, self).save(**kwargs)
                    users = set([uo.user for uo in self.userorder_set.all()])
                    for u in users:
                        body = """
Hey {name},

We are sorry to let you know that the order from {place} has been cancelled!

{reason}

Cheers,
--
4lunch.eu

To cancel notifications, visit this address: http://whats.4lunch.eu{cancel_url}
                """.format(name=u.username, place=self.provider.name, cancel_url=reverse_lazy('notifications'),
                           reason='The reason given is: '+self.cancelled_reason  if self.cancelled_reason else 'No reason was given by the manager')
                        send_mail("What's for lunch? - 4lunch.eu", body,
                                  '4lunch.eu notifications <notifications@4lunch.eu>',
                                  [u.email], fail_silently=True)

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
        return u"{0} from {1}".format(self.name, self.provider.name)

    class Meta(object):
        ordering = ['order']


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
    all_outings = models.BooleanField(default=False)

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


class Company(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    company = models.ForeignKey(Company)


class UserInvite(models.Model):
    email = models.EmailField()
    secret = models.CharField(primary_key=True, max_length=32, editable=False)
    company = models.ForeignKey(Company)
    used_on = models.DateTimeField(editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.secret = str(uuid.uuid4())[:32]
        return super(UserInvite, self).save(*args, **kwargs)

