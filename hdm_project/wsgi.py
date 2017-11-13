import os
import sys

path='/var/www/django_hdm'

if path not in sys.path:
  sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_hdm.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

