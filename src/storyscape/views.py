import commands
import os
import random
import logging 
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

from django.template.loader import render_to_string
from django.conf import settings
from tagging.models import TaggedItem, Tag
import simplejson

from storyscape.models import Story, PageMediaObject, Page
from storyscape import utilities
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

def create_download_media(pmo, story):
    dload_url = story.creator_name+'/'
    dload_url += story.title.replace(" ", "_") + '/'
    if not os.path.exists(os.path.join(settings.STORYSCAPE_IMAGE_URL_ROOT, dload_url)): 
        os.makedirs(os.path.join(settings.STORYSCAPE_IMAGE_URL_ROOT, dload_url))  

    png_url = pmo.media_object.url
    png_url = png_url.replace('/mod/', '/org/')
    svg_url = png_url.replace('/png/', '/svg/').replace('.png', '.svg')
    jpg_url = png_url.replace('/png/', '/jpg/').replace('.png', '.jpg')
    not_svg = False
    try:
        svg_mo = MediaObject.objects.get(url=svg_url)
        url = svg_mo.url
    except MediaObject.DoesNotExist:
        url = png_url
        not_svg = True
    if not_svg: 
        try:
            jpg_mo = MediaObject.objects.get(url=jpg_url)
            url = jpg_mo.url
        except MediaObject.DoesNotExist:
            url = png_url

    #if there is a svg file to use for image resize/creation use it 
    if url[len(url)-3:].lower() == 'svg':          
        dload_url += "/" + os.path.split(url)[1][:-3]+'png'
    elif url[len(url)-3:].lower() == 'jpg': 
        dload_url += "/" + os.path.split(url)[1][:-3]+'png'
    else:
        dload_url += "/" + os.path.split(url)[1]
        
    # if the file already exists we want to create a different named file
    for _ in range(0,10):
        if os.path.exists(settings.STORYSCAPE_IMAGE_URL_ROOT+dload_url) or PageMediaObject.objects.filter(download_media_url=dload_url).count():
            dload_url = dload_url[:-4]+"_"+str(random.randint(0,100000))+".png"
        else: 
            break
        pmo.download_media_url = dload_url
    # convert -background none -resize 800x200\! railroad.svg +antialias railroad.png
    cmd_str = 'convert -background none '+ settings.MEDIALIBRARY_URL_ROOT+ url +' -resize '
    cmd_str += str(pmo.width) +'x'+ str(pmo.height)+'\! +antialias png32:'+ settings.STORYSCAPE_IMAGE_URL_ROOT+dload_url
    commands.getoutput(cmd_str)
    pmo.download_media_url = dload_url

def populate_pmo_from_json(pmo_json, z_index, story, page, existing_pmo):
    
    
    if not existing_pmo:
        pmo = PageMediaObject(page = page)
        pmo.save() # TODO: unnecessary write to DB
    
    if pmo_json.get("type") == "image":
        mo = MediaObject.objects.get(id=pmo_json.get("object_id"))
        pmo.media_object = mo
    elif pmo_json.get("type") == 'text':
            
        pmo.font_size = pmo_json.get('font_size', pmo.font_size)
        pmo.font_color = pmo_json.get('color', pmo.font_color)

    pmo.anime_code = pmo_json.get('action_code',pmo.anime_code)
    pmo.animate_on = pmo_json.get('action_trigger_code',pmo.animate_on)
    pmo.goto_page = pmo_json.get('page_on_touch',pmo.goto_page)
    if not pmo.goto_page:
        pmo.goto_page = -1
    pmo.reaction_object = 'none' 
    pmo.xcoor = pmo_json.get('x',pmo.xcoor)
    pmo.ycoor = pmo_json.get('y',pmo.ycoor)
    pmo.z_index = z_index
    pmo.width = pmo_json.get('width',pmo.width)
    pmo.height = pmo_json.get('height',pmo.height)
    pmo.assoc_text = pmo_json.get('text',pmo.assoc_text)
    pmo.media_type = pmo_json.get('type',pmo.media_type)
    pmo.page = page

    
    pmo.save()
    
    return pmo

def story_to_dict(story):
    tmp = {}
    tmp["story_id"] = story.id
    tmp["title"] = story.title
    tmp["creator_uid"] = story.creator_uid
    tmp["author_name"] = story.creator_name
    tmp["genre"] = story.genre
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
        for pmo in page.pagemediaobject_set.select_related('media_object').all():
            page_json['media_objects'].append(pmo_to_json(pmo))
        story_dict['pages'].append(page_json)
    
    return simplejson.dumps(story_dict)

def index(request):
    return render_to_response('public/index.html', 
                              dict(), 
                              context_instance=RequestContext(request))

@login_required
@ajax_required
@require_POST
def save_story(request):

    user = request.user
    print request.POST
    story_json = simplejson.loads(request.POST.get("story"))


    story_id = story_json.get("story_id")
    if story_id:
        story = Story.objects.get(id=story_id)
    else:
        story = Story(creator_uid = request.user.id)
        story.save() # TODO: unnecessary write
        story.users.add(user)

    story.title = story_json.get("title",story.title)
    story.genre = story_json.get("genre",story.genre)
    story.description = story_json.get("description",story.description)
    story.tags.delete()
    story.tags = story_json.get("tags","")
    story.creator_name = user.username
    
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
    msg = 'something unhelpful went wrong'
    
    story = Story.objects.get(id=request.POST['story_id'])
            
    story.is_published = False 

    file_save_path = story.get_filesave_path()
    
    utilities.remove_dir_files(file_save_path, []) 
    
    pmos = PageMediaObject.objects.filter(page__story = story, media_type='image')
    
    for pmo in pmos:
        print pmo
        create_download_media(pmo, story)
        pmo.save()
    
    
    utilities.create_story_thumbnail(story, file_save_path)
    story.save()
    try: 
        utilities.story_to_xml(story, file_save_path)
    except IOError:
        msg = 'error creating xml version of story'
        story.is_published = False 
        
    utilities.create_story_nomedia_file(file_save_path)
    if not utilities.create_story_thumbnail(story, file_save_path):
        msg = 'error creating thumbnail'
        story.is_published = False 
    
    if not utilities.create_story_zip(story, file_save_path):
        msg = 'error creating downloadable media'
        story.is_published = False
    else: 
        story.is_published = True
    
    story.save()

    return HttpResponse(msg)


@login_required
@ajax_required
@require_POST
def delete_story(request):
    story_id = request.POST.get('story_id')
    story = Story.objects.get(id=story_id)
    story.delete()
    return HttpResponse(dict(success = True))


@login_required
@ajax_required
@require_GET
def get_user_stories(request):
    user = request.user
    
    stories = Story.objects.filter(users=user).filter(creator_uid=user.id).order_by('creation_datetime')    

    stories_json = story_list_to_json(stories)

    return HttpResponse(stories_json)


@ajax_required
@require_GET
def load_story(request):
    story = Story.objects.get(id=request.GET.get("story_id"))    
    
    story_json = story_to_json(story)
    
    return HttpResponse(story_json)

@login_required
def create_story(request, story_id=None):
    
    user = request.user 
    
    story= None    
    if story_id:
        try:
            story = Story.objects.get(id=story_id, creator_uid=user.id)
        except:
            raise Http404

    ml = MediaLibrary.objects.get(user=user)
    media_objects = ml.media_object.filter(Q(format__label='png') | Q(format__label='jpg')).order_by('-id')[:NUM_ITEMS_PER_PAGE]

    
    return render_to_response('storyscape/create.html',
                 {'user': request.user, 
                  'story': story,
                  'show_favorites_library': True,
                  "media_objects": media_objects,
                  'action_codes':ACTION_CODES,
                  'action_trigger_codes':ACTION_TRIGGER_CODES},
                 context_instance=RequestContext(request))

def stories_library(request):
    return render_to_response('storyscape/stories_library.html', 
                              dict(), 
                              context_instance=RequestContext(request))


@ajax_required
@require_GET
def get_stories(request):
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
        query = query.filter(is_published = True)
    
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
    return render_to_response('storyscape/about_reader.html', 
                              {}, 
                              context_instance=RequestContext(request))

def story_preview(request, story_id):
    story = Story.objects.get(id=story_id)
    return render_to_response('storyscape/story_preview.html', 
                              dict(story=story,
                                   action_codes=ACTION_CODES,
                                   action_trigger_codes=ACTION_TRIGGER_CODES,
                                   from_page=request.GET.get("from","")),
                              context_instance=RequestContext(request) )
