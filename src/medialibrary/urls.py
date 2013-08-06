from django.conf.urls.defaults import patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^images/$', 'medialibrary.views.index', name='media_library'),
    url(r'^image_upload/$', 'medialibrary.views.image_upload', name='media_image_upload'),
    url(r'^toggle_favorite_mo/$', 'medialibrary.views.toggle_favorite_media_object', name='toggle_favorite_mo'),
    url(r'^get_media_objects/$', 'medialibrary.views.get_media_objects', name='get_media_objects'),
    
    url(r'^toggle_visible/$', 'medialibrary.views.toggle_media_object_visibility', name='toggle_media_object_visibility'),
)
