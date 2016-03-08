import registration
from django.contrib.auth import user_logged_out
from django.db.models import Q
from registration import signals
from django.contrib import messages
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from app.models import Order, NotificationRequest, FeedEntry


@receiver(post_save, sender=Order)
def notify_all(**kwargs):
    order = kwargs['instance']
    if not kwargs['created'] or order.silent:
        return
    nrs = NotificationRequest.objects.filter(Q(providers__in=[order.provider]) | Q(all_providers=True)).distinct()
    for nr in nrs:
        body = """
Hey {name},

An order that matches your notification criteria has been created!
Check it out on https://whats.4lunch.eu !

Cheers,
--
4lunch.eu

To cancel notifications, visit this address: https://whats.4lunch.eu{cancel_url}
        """.format(name=nr.user.username, cancel_url=reverse_lazy('notifications'))
        send_mail("What's for lunch? - 4lunch.eu", body, '4lunch.eu notifications <notifications@4lunch.eu>',
            [nr.user.email], fail_silently=True)


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
