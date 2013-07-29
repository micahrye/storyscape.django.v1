from django.conf.urls.defaults import patterns, url, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('storyscape.views',

    url(r'^create/$', 'storyscape', name='storyscape'), 
    (r'^storyinfo/$', 'storyscapeBookInfo'),
    (r'^my_stories/$', 'personalStoryLib'),
    url(r'^get_story/$', 'get_story', name='storyscape_get_story'),
    #(r'^mobileupload/$', 'mobile_upload'),
    #(r'^(?P<poll_id>\d+)/details/$', 'detail'),
    
    
    url(r'^preview/(?P<story_id>\d+)/$', include('storyscape_stills.urls')),
    url(r'^reader/$', 'reader_info', name="reader_info"),

)
