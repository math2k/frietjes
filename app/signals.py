import registration
from django.contrib.auth import user_logged_out
from django.db.models import Q
from registration import signals
from django.contrib import messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from app.models import Order, NotificationRequest, FeedEntry, UserInvite, EatingGroup


@receiver(post_save, sender=Order)
def send_order_notifications(**kwargs):
    order = kwargs['instance']
    if not kwargs['created'] or order.silent:
        return
    nrs = NotificationRequest.objects.filter(Q(providers__in=[order.provider]) | Q(all_providers=True)).distinct()
    for nr in nrs:
        if nr.user == order.manager:
            continue
        if nr.user.profile.company != order.company:
            continue
        body = """
Hey {name},

An order at {place} has been created!

Check it out on https://whats.4lunch.eu !

Cheers,
--
4lunch.eu

To cancel notifications, visit this address: https://whats.4lunch.eu{cancel_url}
        """.format(place=order.provider.name, name=nr.user.username, cancel_url=reverse_lazy('notifications'))
        send_mail("What's for lunch? - 4lunch.eu", body, '4lunch.eu notifications <notifications@4lunch.eu>',
            [nr.user.email], fail_silently=True)


@receiver(post_save, sender=EatingGroup)
def send_eatinggroup_notifications(**kwargs):
    eg = kwargs['instance']
    if not kwargs['created'] or eg.silent:
        return
    nrs = NotificationRequest.objects.filter(Q(providers__in=[eg.provider]) | Q(all_outings=True)).distinct()
    for nr in nrs:
        if nr.user == eg.manager:
            continue
        if nr.user.profile.company != eg.company:
            continue
        body = """
Hey {name},

A group outing to {place} has been created!

Check it out on https://whats.4lunch.eu !

Cheers,
--
4lunch.eu

To cancel notifications, visit this address: https://whats.4lunch.eu{cancel_url}
        """.format(place=eg.provider.name, name=nr.user.username, cancel_url=reverse_lazy('notifications'))
        send_mail("What's for lunch? - 4lunch.eu", body, '4lunch.eu notifications <notifications@4lunch.eu>',
            [nr.user.email], fail_silently=True)


@receiver(post_save, sender=UserInvite)
def notify_all(**kwargs):
    invite = kwargs['instance']
    if not kwargs['created']:
        return
    body = """
Hey there,

You have been invited to join 4lunch.eu.

Create your account by following this personalized link:
https://whats.4lunch.eu{register_url}

Cheers,
--
4lunch.eu
        """.format(register_url=reverse_lazy('registration_register', kwargs={'secret': invite.secret}))
    send_mail("What's for lunch? - 4lunch.eu", body, '4lunch.eu notifications <notifications@4lunch.eu>',
        [invite.email], fail_silently=True)


@receiver(post_save)
def add_feedentry(**kwargs):
    if kwargs['sender'] == Order:
        if not kwargs['created']:
            return
        fe = FeedEntry(event='An order at _{0}_ has been opened'.format(kwargs['instance'].provider.name))
        fe.save()


@receiver(registration.signals.user_registered)
def signal_all(**kwargs):
    messages.success(kwargs['request'], 'Your account has been created, and you\'re already logged in, how cool is that ?')


@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    messages.success(request, "You've been logged out, see ya!")
