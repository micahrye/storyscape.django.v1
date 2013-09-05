from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('storyscape.views',

    url(r'^$', 'stories_library', name='stories_library'),
    url(r'^edit/(?P<story_id>\d+)/$', 'create_story', name='edit_story'),
    url(r'^create/$', 'create_story', name='create_story'), 
    url(r'^my_stories/$', 'get_user_stories', name='get_user_stories'),

    url(r'^stories/$', 'get_stories', name='get_stories'), 
    url(r'^toggle_visible/$', 'toggle_story_visibility', name='toggle_story_visibility'),

    url(r'^checktasks/$', 'check_finished_tasks', name='check_finished_tasks'), 
    
    url(r'^delete/$', 'delete_story', name='delete_story'), 
    url(r'^save/$', 'save_story', name='save_story'), 
    url(r'^load/$', 'load_story', name='load_story'), 
    url(r'^publish/$', 'publish_story', name='publish_story'), 
    
    url(r'^preview/(?P<story_id>\d+)/$', 'story_preview', name="story_preview"),
    url(r'^aboutreader/$', 'reader_info', name="reader_info"),

    url(r'^storylist/$', 'story_download_list', name='story_download_list'),
    url(r'^download/(?P<story_id>\d+)/(?P<zip_name>.*)', 'download_story', name='download_story'),
)
