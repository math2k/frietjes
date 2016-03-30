from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail, EmailMessage
from django.core.urlresolvers import reverse_lazy


class Command(BaseCommand):
    help = 'Send a test notification email'

    def handle(self, *args, **kwargs):
        body = """
Hey {name},

An order that matches your notification criteria has been created!
Check it out on https://whats.4lunch.eu !

Cheers,
--
4lunch.eu

To cancel notifications, visit this address: https://whats.4lunch.eu{cancel_url}
        """.format(name='Test user', cancel_url=reverse_lazy('notifications'))
        email = EmailMessage('Notification test', body, 'notifications@4lunch.eu', ['math2k@gmail.com'], headers={'List-Unsubscribe': '{0}{1}'.format('https://whats.4lunch.eu', reverse_lazy('notifications'))})

        email.send(fail_silently=False)
