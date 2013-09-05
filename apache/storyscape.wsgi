import os
import sys
import site

site.addsitedir('/var/www/storyscape/storyscape-env/lib/python2.7/site-packages')
 
path = '/var/www/storyscape/storyscape.django/src'
if path not in sys.path:
    sys.path.insert(0, path)

import djcelery
djcelery.setup_loader()
 
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

