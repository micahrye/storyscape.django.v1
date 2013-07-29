from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('storyscape_stills.views',

    url(r'^$', 'storyscape_stills', 
      {}, 
      name='storyscape_stills'), 
)
