from django.conf.urls.defaults import patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('storyscape.views',

    url(r'^edit/(?P<story_id>\d+)/$', 'create_story', name='edit_story'),
    url(r'^create/$', 'create_story', name='create_story'), 
    url(r'^my_stories/$', 'get_user_stories', name='get_user_stories'),
    
    url(r'^delete/$', 'delete_story', name='delete_story'), 
    url(r'^save/$', 'save_story', name='save_story'), 
    url(r'^load/$', 'load_story', name='load_story'), 
    url(r'^publish/$', 'publish_story', name='publish_story'), 
    
    url(r'^preview/(?P<story_id>\d+)/$', 'story_preview'),
    url(r'^reader/$', 'reader_info', name="reader_info"),

)
