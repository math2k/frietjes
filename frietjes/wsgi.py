"""
WSGI config for matttew project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import sys
import site

PROJECT_ROOT = os.path.dirname(__file__)
VIRTUALENV_PATH = '/var/www/frietjes.math2k.net/python/lib/python2.7/site-packages'
# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
os.environ["DJANGO_SETTINGS_MODULE"] = "frietjes.settings"
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "q.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
prev_sys_path = list(sys.path)
site.addsitedir(VIRTUALENV_PATH)

path = os.path.join(PROJECT_ROOT, '..')
if path not in sys.path:
  sys.path.append(path)

new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

path = os.path.join(PROJECT_ROOT, "..")
if path not in sys.path:
  sys.path.append(path)
# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)



#import newrelic.agent
#newrelic.agent.initialize(os.path.join(PROJECT_ROOT, 'matttew', 'newrelic.ini'))
