import commands
import os
import random
import logging, subprocess
from collections import OrderedDict

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from django.db.models import Q


from django.db.models.query import QuerySet
from decorators import ajax_required
from django.views.decorators.http import require_POST, require_GET
from django.core.urlresolvers import reverse

from django.template.loader import render_to_string
from django.conf import settings
from tagging.models import TaggedItem, Tag
import simplejson

from storyscape.models import Story, PageMediaObject, Page, StoryDownload, DEFAULT_STORY_GENRE
from storyscape import utilities
from storyscape import tasks

from medialibrary.models import MediaLibrary, MediaObject
from medialibrary.views import NUM_ITEMS_PER_PAGE

logger = logging.getLogger(__name__)
NUM_TAGS_PER_PAGE = 20

ACTION_TRIGGER_CODES = OrderedDict([('Touch', 1),
                        ('Sound', 2),
                       ])

ACTION_CODES = OrderedDict([('Fade Out',105),
                ('Toggle Fade',113),
                ('Expand',102),
                ('Shrink',103),
                ('Expand-Shrink',104),
                ('Horizontal Shake',114),
                ('Vertical Shake',115),
                ('Jump',107),
                ('Spin',112),
                ('Drag',110),
                ('Rubberband',111),
                ('Slide Left',116),
                ('Slide Right',101),
                ]);

KINECT_TRIGGER_CODES = OrderedDict([ ('Jump', 500), 
                                    ('Wave', 501),
                                    ('Nod', 502), ])

GOTO_PAGE_ACTION_CODE = 200



def populate_pmo_from_json(pmo_json, z_index, story, page, existing_pmo):
    
    
    if not existing_pmo:
        pmo = PageMediaObject(page = page)
        pmo.save() # TODO: unnecessary write to DB
    
    if pmo_json.get("type") == "image":
        mo = MediaObject.objects.get(id=pmo_json.get("object_id"))
        pmo.media_object = mo
    elif pmo_json.get("type") == 'text':
            
        pmo.font_size = pmo_json.get('font_size') or pmo.font_size
        pmo.font_color = pmo_json.get('color') or pmo.font_color
        
        if len(pmo.font_color) == 4:
            # we have the format #CCC and we need #CCCCCC
            pmo.font_color = "".join(["{0}{0}".format(x) for x in pmo.font_color])[1:]

    pmo.anime_code = pmo_json.get('action_code') or pmo.anime_code
    pmo.animate_on = pmo_json.get('action_trigger_code') or pmo.animate_on
    pmo.goto_page = pmo_json.get('page_on_touch') or pmo.goto_page
    
    if pmo.goto_page > -1:
        pmo.anime_code = GOTO_PAGE_ACTION_CODE
    
    pmo.reaction_object = 'none' 
    pmo.xcoor = pmo_json.get('x') or pmo.xcoor
    pmo.ycoor = pmo_json.get('y') or pmo.ycoor
    pmo.z_index = z_index
    pmo.width = pmo_json.get('width') or pmo.width
    pmo.height = pmo_json.get('height') or pmo.height
    pmo.assoc_text = pmo_json.get('text') or pmo.assoc_text
    pmo.custom_commands = pmo_json.get('custom_commands') or pmo.custom_commands
    pmo.media_type = pmo_json.get('type') or pmo.media_type
    pmo.page = page    
    pmo.save()
    
    return pmo

def story_to_dict(story):
    tmp = {}
    tmp["story_id"] = story.id
    tmp["title"] = story.title
    tmp["creator_uid"] = story.creator_uid
    tmp["author_name"] = story.creator_name
    tmp["description"] = story.description
    tmp["tags"] = [tag.name for tag in story.tags]
    tmp["num_pages"] = story.page_set.count()
    return tmp

def story_list_to_json(story_objects):
    stories_list = []
    
    # if single story object passed in, not a list, then make it into a list
    if not story_objects.__class__ == list and not story_objects.__class__ == QuerySet:
        story_objects = [story_objects]
    
    for story in story_objects: 
        stories_list.append(story_to_dict(story))
        
        
    return simplejson.dumps(stories_list)


def pmo_to_json(pmo):
    
    pmo_json = dict(object_id = pmo.media_object_id,
                    type = pmo.media_type,
                    font_size = pmo.font_size,
                    color = pmo.font_color,
                    action_code = pmo.anime_code,
                    action_trigger_code = pmo.animate_on,
                    page_on_touch = pmo.goto_page,
                    x = pmo.xcoor,
                    y = pmo.ycoor,
                    z_index = pmo.z_index,
                    width = pmo.width,
                    height = pmo.height,
                    text = pmo.assoc_text,
                    custom_commands = pmo.custom_commands,
                    )
    if pmo.media_object:
        pmo_json['url'] = settings.MEDIA_URL + pmo.media_object.url
    return pmo_json


def story_to_json(story):
    
    story_dict = story_to_dict(story)
    story_dict['pages'] = []
    
    for page in Page.objects.filter(story=story).order_by("page_number"):
        page_json = dict(page_number = page.page_number,
                         page_id = page.id,
                         media_objects = [])
        for pmo in page.pagemediaobject_set.select_related('media_object').order_by("z_index").all():
            page_json['media_objects'].append(pmo_to_json(pmo))
        story_dict['pages'].append(page_json)
    
    return simplejson.dumps(story_dict)

def index(request):
    '''
    Public splash page
    '''
    return render_to_response('public/index.html', 
                              dict(), 
                              context_instance=RequestContext(request))


@ajax_required
@login_required
@require_POST
def toggle_story_visibility(request):
    user = request.user
    story_id = request.POST['STORY_ID']
    
    story = Story.objects.get(id=story_id, creator_uid=user.id)

    # when you save an Story, the tagging library clears the tags. this is a hack to get around that stupid behavior.
    tags = Tag.objects.get_for_object(story)
    tag_string = ",".join(['"{0}"'.format(tag.name) for tag in tags])
    
    story.is_public = not story.is_public
    story.save()
    
    Tag.objects.update_tags(story, tag_string)
    
    return HttpResponse(simplejson.dumps(dict(is_visible = story.is_public)))


@login_required
@ajax_required
@require_POST
def save_story(request):
    '''
    Called from the Create page
    '''
    user = request.user
    story_json = simplejson.loads(request.POST.get("story"))
    story_type = request.POST.get('story_type', 'standard')

    story_id = story_json.get("story_id")
    if story_id:
        story = Story.objects.get(id=story_id)
    else:
        story = Story(creator_uid = request.user.id)
        story.save() # TODO: unnecessary write
        story.users.add(user)

    story.title = story_json.get("title",story.title)
    story.genre = DEFAULT_STORY_GENRE
    story.description = story_json.get("description",story.description)
    
    story.tags = story_json.get("tags","")
    story.creator_name = user.username
    story.story_type = story_type
    
    # a list of pages, and each page is a list of media objects
    pages_info = story_json.get("pages")

    page_ids = []
    for page in pages_info:
        if (page.get('page_id')):
            page_ids.append(page.get('page_id'))
    Page.objects.filter(story=story).exclude(id__in=page_ids).delete()
    
    for page_number, page_json in enumerate(pages_info):
        page = None
        if page_json.get('page_id'):
            try:
                page = Page.objects.filter(story=story).get(id=page_json.get('page_id'))
            except Page.DoesNotExist:
                pass
        page = page or Page(story=story)
            
        page.page_number = page_number
        page.save()
            
        pagemediaobject_ids = []
        for pmo in page_json['media_objects']:
            try:
                if (pmo.get('pagemediaobject_id')):
                    pagemediaobject_ids.append(pmo.get('pagemediaobject_id'))
            except KeyError:
                pass
        page.pagemediaobject_set.exclude(id__in=pagemediaobject_ids).delete()
        
        existing_pmos = dict([(pmo.id, pmo) for pmo in page.pagemediaobject_set.all()])
        
        for pmo_number, pmo_json in enumerate(page_json['media_objects']):
            populate_pmo_from_json(pmo_json, pmo_number, story, page, existing_pmos.get(pmo_json.get('pagemediaobject_id')))
    
    story.save()
        
    return HttpResponse(simplejson.dumps(dict(success=True,story_id=story.id)))

@login_required
@ajax_required
@require_POST
def publish_story(request):
    '''
    Called from the create page
    '''
    
    story = Story.objects.get(id=request.POST['story_id'])
    
    if story:
        '''
        this line will error becase static code-analsys only sees what 
        you see, not runtime info that would result in delay being there. 
        You may want to change eclipse settings to ignore this. 
        Window -> Preferences -> PyDev -> Editor -> Code Analysis -> Imports -> Import not found -> Ignore
        '''
        if not settings.DEBUG: 
            result = tasks.publish_story.delay(story.id)
            queued_tasks = request.session.get('queued_tasks', [])
            queued_tasks.append(result)
            request.session['queued_tasks'] = queued_tasks
        else: 
            tasks.publish_story(story.id)
  
    return HttpResponse('success')

@login_required
@ajax_required
@require_GET
def check_finished_tasks(request):
    '''
    This gets called once per page load if the user is logged in, and periodically after that if (a) the user has queued a task, or (b) there are tasks that have been queued
    '''
    queued_tasks = request.session.get('queued_tasks', [])
    
    still_queued_tasks = []
    finished_messages = []
    
    if queued_tasks:
        for result in queued_tasks:
            if result.ready():
                if result.successful():
                    finished_messages.append(['success',result.result])
                else:
                    finished_messages.append(['error',"Sorry, there was an issue with the story publishing... We're looking into it!"])
            else:
                still_queued_tasks.append(result)
        
        request.session['queued_tasks'] = still_queued_tasks
    
    return HttpResponse(simplejson.dumps(dict(has_tasks = bool(still_queued_tasks), finished_messages = finished_messages)))



@login_required
@ajax_required
@require_POST
def delete_story(request):
    '''
    Called from the create page
    '''
    
    story_id = request.POST.get('story_id')
    story = Story.objects.get(id=story_id)
    story.delete()
    return HttpResponse(dict(success = True))


@login_required
@ajax_required
@require_GET
def get_user_stories(request):
    '''
    Called from the create page when loading a new story
    '''
    
    user = request.user
    
    stories = Story.objects.filter(users=user).filter(creator_uid=user.id).order_by('-creation_datetime')    

    stories_json = story_list_to_json(stories)

    return HttpResponse(stories_json)


@ajax_required
@require_GET
def load_story(request):
    '''
    Called from the create page
    '''
    
    story = Story.objects.get(id=request.GET.get("story_id"))    
    
    story_json = story_to_json(story)
    
    return HttpResponse(story_json)


@login_required
def create_kinect_story(request, story_id=None):
    
    rtn_data = create_story(request, story_id, True)
    rtn_data['action_trigger_codes'] = KINECT_TRIGGER_CODES 
    
    return render_to_response( 'storyscape/create_kinect.html', rtn_data, 
                               context_instance=RequestContext(request) )

@login_required
def create_story(request, story_id=None, kinect=False):
    '''
    Called from the create page to save a story. contrary to the name, can be used to save an existing story. um, sorry.
    '''
    
    user = request.user 
    
    story = None    
    if story_id:
        try:
            story = Story.objects.get(id=story_id, creator_uid=user.id)
        except:
            raise Http404

    ml = MediaLibrary.objects.get(user=user)
    media_objects = ml.media_object.filter(Q(format__label='png') | Q(format__label='jpg')).order_by('-id')[:NUM_ITEMS_PER_PAGE]
    
    rtn_data = {'user': request.user, 
                  'story': story,
                  'show_favorites_library': True,
                  "media_objects": media_objects,
                  'action_codes':ACTION_CODES,
                  'action_trigger_codes':ACTION_TRIGGER_CODES}
    if kinect:
        return rtn_data
    
    return render_to_response('storyscape/create.html',
                 rtn_data,
                 context_instance=RequestContext(request))

def stories_library(request):
    '''
    A list of all the stories
    '''
    return render_to_response('storyscape/stories_library.html', 
                              dict(), 
                              context_instance=RequestContext(request))


@ajax_required
@require_GET
def get_stories(request):
    '''
    Called from the stories library
    '''
    
    page_number = int(request.GET.get('PAGE_NUMBER', 1))
    search_term = request.GET.get('SEARCH_TERM', '')
    get_all = request.GET.get('GET_ALL', 'true') == 'true'
    
    if search_term:
        tag_query = Tag.objects.filter(name__icontains=search_term)
        query = TaggedItem.objects.get_union_by_model(Story, tag_query)
    else:
        query = Story.objects

    if request.user.is_authenticated() and not get_all:
        query = query.filter(creator_uid = request.user.id)
    else:
        query = query.filter(is_published = True, is_public = True)
    
    objs = query.order_by('-id').all()
    
    paginator = Paginator(objs, NUM_ITEMS_PER_PAGE)
    
    page_number = min(paginator.num_pages, page_number)
    stories = paginator.page(page_number).object_list
    
    content = render_to_string("storyscape/stories_paginated_content.html", dict(stories = stories,
                                                  paginator = paginator), 
                                                  context_instance=RequestContext(request))
    
    return HttpResponse(simplejson.dumps(dict(pages = paginator.num_pages,
                                              current_page = page_number,
                                              content = content)))
    

def reader_info(request):
    '''
    A static page with information about the reader
    '''
    return render_to_response('storyscape/about_reader.html', 
                              {}, 
                              context_instance=RequestContext(request))

def story_preview(request, story_id):
    '''
    A page that lets you preview a story
    '''
    
    story = Story.objects.get(id=story_id)
    return render_to_response('storyscape/story_preview.html', 
                              dict(story=story,
                                   action_codes=ACTION_CODES,
                                   action_trigger_codes=ACTION_TRIGGER_CODES,
                                   from_page=request.GET.get("from","")),
                              context_instance=RequestContext(request) )


def api_list_stories(request, story_type='kinect'):
    
    search_term = request.GET.get("search")
    
    stories = Story.objects.filter(is_published=True).filter(story_type=story_type)

    if search_term:
        stories = stories.filter(Q(title__contains=search_term) | Q(creator_name__contains=search_term))

    stories = story_list_to_json(stories)
    if 'callback' in request.REQUEST:
        stories = request.REQUEST['callback'] + '('+stories+');'
        return HttpResponse(stories, mimetype='application/json') 
    
    return HttpResponse( stories )


@require_GET
def api_get_story(request): 
    
    story_id = request.GET.get('STORY_ID', -1)
    if 'STORY_ID' in request.GET:
        try: 
            story = Story.objects.get(id=story_id)
        except Story.DoesNotExist:
            return HttpResponse('story id does not exist')
        story = story_to_json(story)
        '''
        If the request is for jsonp we handle it here
        '''
        if 'callback' in request.REQUEST:
            story = request.REQUEST['callback'] + '('+story+');'
            return HttpResponse(story, mimetype='application/json') 
        return HttpResponse( story )    
    
    return HttpResponse("nothing to see here")


@require_GET
def download_story(request, story_id, zip_name):
    '''
    Used to log downloads of story zips, it serves the zip files to the app
    
    the reason the zip name is at the end, and we're not using GET parameters for the story name is
    because the app expects the download url to end with the zip name after a slash
    '''
    
    user_id = request.GET.get("user_id")
    device_id = request.GET.get("device_id","")
    
    story = Story.objects.get(id=story_id)
    
    story_download = StoryDownload(device_id = device_id,
                                   user_id = user_id,
                                   story = story)
    story_download.save()
    
    
    path = os.path.join(story.get_filesave_path(), story.get_zip_name())
    
    response = HttpResponse()
    response['Content-Type'] = ''
    response['X-Sendfile'] = (os.path.join(settings.MEDIA_ROOT, path)).encode('utf-8')
    return response

def get_download_url(story):
    return settings.SITE_URL + reverse("download_story", kwargs = dict(zip_name = story.get_zip_name(), story_id = story.id))

@require_GET
def story_download_list(request):
    '''
    Called from the app to show all the stories available for download
    '''

    search_term = request.GET.get("search")
    
    stories = Story.objects.filter(is_published=True, is_public = True)

    if search_term:
        stories = stories.filter(Q(title__contains=search_term) | Q(creator_name__contains=search_term))
    
    download_urls = ", ".join([get_download_url(story) for story in stories])
    return HttpResponse(download_urls)

def download_reader_app(request):
    return render_to_response('storyscape/reader_app.html', {}, context_instance=RequestContext(request))
