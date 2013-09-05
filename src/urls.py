from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'storyscape.views.home', name='home'),
    # url(r'^storyscape/', include('storyscape.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^storyscape/', include('storyscape.urls')),
    
    url(r'^medialibrary/', include('medialibrary.urls')),

    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts', redirect_to, {'url': '/accounts/register/'}),
    url(r'^$', 'storyscape.views.index', name='index'),
    
    url(r'^download/app/storyscape/$', 'storyscape.views.download_reader_app'),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
