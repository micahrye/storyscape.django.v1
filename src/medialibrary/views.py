import datetime
import random 
import os
import commands

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from decorators import ajax_required
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings

from django.core import serializers
from itertools import chain
import simplejson

from tagging.models import TaggedItem, Tag
from tagging.utils import LOGARITHMIC

from medialibrary.models import MediaLibrary, MediaObject, ImageUploadForm2, MediaFormat, MEDIAOBJECT_max_length_name, MediaType
from storyscape.models import Story

NUM_ITEMS_PER_PAGE = 15
NUM_TAGS_PER_PAGE = 50


def search_stories(search_term):
    ''' IMPORTANT: 
        need to consider non-alphanumeric characters, need to consider
        code injection vulnerablity 
    '''
    if search_term == "":
        #need to change the following line, just a tmp fix
        return Story.objects.filter(is_published=True)

    #qt1 = Tag.objects.filter(name=search_term)
    #stories1 = TaggedItem.objects.get_union_by_model(Story, qt1).filter(creator_name='micahrye')    
    qt2 = Tag.objects.filter(name__icontains=search_term)
    stories2 = TaggedItem.objects.get_union_by_model(Story, qt2)
    # compine the two querysets into one list
    stories = list(chain([], stories2))
    #print "The stories are ", stories
    return stories




def get_most_common_tags(num_tags):
    tags = Tag.objects.cloud_for_model(MediaObject, 
                            steps=6, distribution=LOGARITHMIC, filters=None, min_count=30)
    
    return tags, get_random_tags(tags, num_tags)[0:num_tags]

def get_popular_tags(num_tags, count=100):
    tags = Tag.objects.cloud_for_model(MediaObject, 
                            steps=6, distribution=LOGARITHMIC, filters=None, min_count=count)
    tags = sorted(tags, key=lambda tag: tag.count, reverse=True)  
    nrp = num_tags/4 #number random popular 
    rpt = get_random_tags(tags, nrp) 
    
    rtn_tags = tags[:(num_tags-nrp)] + rpt
    return rtn_tags

def get_random_tags(tags, NUM_TAGS_PER_PAGE):
    num_tags = len(tags)
    if NUM_TAGS_PER_PAGE > num_tags:
        return tags
    
    rtn_tags = []
    for index in random.sample(range(num_tags), NUM_TAGS_PER_PAGE):
        rtn_tags.append(tags[index])
    return rtn_tags

def get_random_set_mediaobjects(num_mo_rtn): 
    mediaobjects = MediaObject.objects.filter(format__label='png')
    num_mo = mediaobjects.count()
    if num_mo_rtn > num_mo:
        return mediaobjects
    
    rtn_mos = []
    for index in random.sample(range(num_mo), num_mo_rtn):
        rtn_mos.append(mediaobjects[index])
    
    return rtn_mos

def serialize_tags(tags):
    stags = []
    for tag in tags: 
        tmp = {}
        tmp['font_size'] = tag.font_size
        tmp['name'] = tag.name   
        tmp['count'] = tag.count
        stags.append(tmp)
        
    return stags



def handle_request(request, request_type):
    """
    Helper function that handles request from medialibrary Images/Stories.

    request_type = a string, which is either "mediaobject" or "story", according to which
    the functions below are written. "mediaobject" is for media objects.

    """
    
    # on first page load present a random set of mediaobjects. 
    #mediaobjects = get_random_set_mediaobjects(NUM_ITEMS_PER_PAGE)
    objs = Story.objects.filter(is_published=True).all()
    paginator = Paginator(objs, NUM_ITEMS_PER_PAGE)
    try:
        objs = paginator.page(1).object_list
    except EmptyPage:
        pass

    return objs


@ajax_required
@login_required
@require_POST
def toggle_favorite_media_object(request):
    user = request.user
    mo_id = request.POST['MEDIA_OBJECT_ID']
    
    ml = MediaLibrary.objects.get(user=user)
    mo = MediaObject.objects.get(id=mo_id)
    
    if mo in ml.media_object.all():
        ml.media_object.remove(mo)
        is_favorite = False
    else:
        ml.media_object.add(mo)
        is_favorite = True
    return HttpResponse(simplejson.dumps(dict(is_favorite = is_favorite)))



def index(request):
    return render_to_response('medialibrary/media_index.html', {}, context_instance=RequestContext(request))

@ajax_required
@require_GET
def get_media_objects(request):
    page_number = int(request.GET.get('PAGE_NUMBER', 1))
    search_term = request.GET.get('SEARCH_TERM', '')
    get_all_images = request.GET.get('GET_ALL_IMAGES', 'true') == 'true'
    need_add_buttons = request.GET.get('NEED_ADD_BUTTONS', 'true') == 'true'
    
    if search_term:
        tag_query = Tag.objects.filter(name__icontains=search_term)
        query = TaggedItem.objects.get_union_by_model(MediaObject, tag_query)
    else:
        query = MediaObject.objects

    library = None
    if not get_all_images:
        library = MediaLibrary.objects.get(user=request.user)
        favorite_ids = library.media_object.values_list('id', flat=True)
        query = query.filter(id__in = favorite_ids)
    
    query = query.filter(original=False).filter(format__label='png').order_by('-id') 
    objs = query.all()
    
    paginator = Paginator(objs, NUM_ITEMS_PER_PAGE)
    
    page_number = min(paginator.num_pages, page_number)
    objs = paginator.page(page_number).object_list
    
    if request.user.is_authenticated():
        object_ids = [obj.id for obj in objs]
        
        if library:
            # we already loaded only the favorites, so anything in the list is a favorite by default
            favorited_ids = object_ids
        else:
            library = MediaLibrary.objects.get(user=request.user)
            favorited_ids = library.media_object.filter(id__in = object_ids).values_list('id', flat=True)

    content = render_to_string("medialibrary/media_content.html", dict(mediaobjects = objs,
                                              favorited_ids = favorited_ids,
                                              need_add_buttons = need_add_buttons,
                                              paginator = paginator), context_instance=RequestContext(request))
    
    return HttpResponse(simplejson.dumps(dict(pages = paginator.num_pages,
                                              current_page = page_number,
                                              content = content)))


def stories(request):
    objs = handle_request(request, "story")
    return render_to_response('medialibrary/stories.html',
                              {'stories':objs}, 
                         context_instance=RequestContext(request))


@login_required
@ajax_required
def image_upload(request):
    
    user = request.user
    form = ImageUploadForm2()
    success = False
    
    if request.method == 'POST':
        
        
        # IMPORTANT!! if svg we need to create an svg and a png mo... WHAT about if there are 
        # no svg for an img when we PUBLISH?
        mo = MediaObject(creator=user)
        ml = MediaLibrary.objects.get_or_create(user=user)[0]
        ''' IMPORTANT
        django ImageField does not allow for SVG files b/c of possible malicious 
        code that could be in the svg/xml. Need to consider how to deal with this
        ''' 
        form = ImageUploadForm2(request.POST, request.FILES, instance=mo)
        valid = form.is_valid()
        if valid:
            ftype = request.FILES['upload_image'].name[-3:].lower()
            
            # IMPORTANT!!! need to change label to match actual match image format
            mf, _ = MediaFormat.objects.get_or_create(label=ftype) 
            mt, _ = MediaType.objects.get_or_create(label="StillImage") 
            mo.creation_datetime = datetime.datetime.today() 
            mo.name = request.FILES['upload_image'].name[:-4][:MEDIAOBJECT_max_length_name-1]
            mo.format = mf
            mo.type = mt
            mo.publisher = 'sodiioo'
            # mo.url gets set inside form.save(), this way we insure that the 
            # url name is unique sice django takes care of the user uploading files
            # with the same file name by appending an int
            form.save()
            mo.original = True
            tags = request.POST['mo_tags'].lower()
            mo.tags = tags
            mo.has_tag = 1
            #THIS represents the original image uploaded, need to make a copy for general use. 
            mo.save()
            
            #now we make sure that our modified image is a PNG
            mod_mo = MediaObject(creator=user)
            mf, _ = MediaFormat.objects.get_or_create(label='png')
            mod_mo.creation_datetime = mo.creation_datetime
            mod_mo.name = mo.name
            mod_mo.format = mf
            mod_mo.type = mt
            mod_mo.publisher = mo.publisher 
            #create new image and assign url
            mod_url = org_url = settings.MEDIALIBRARY_URL_ROOT + mo.url 
            mod_url = mod_url.replace('/org/', '/mod/')
            mod_url = mod_url.replace('/'+ftype+'/', '/png/')
            mod_url = mod_url[:-3] + 'png'
            if not os.path.exists(os.path.split(mod_url)[0]):
                os.makedirs(os.path.split(mod_url)[0])
            # TODO: should probably use PIL instead of convert from commands
            cmd = 'convert -resize 300x300 ' + org_url + ' ' + mod_url
            _ = commands.getoutput(cmd)
            mod_mo.url = mod_url.replace(settings.MEDIALIBRARY_URL_ROOT, '')
            mod_mo.save()
            mod_mo.tags = tags
            # add modified image to personal library 
            ml.media_object.add(mod_mo)
            success = True
            form = ImageUploadForm2()

    result = {'form':render_to_string('medialibrary/image_upload.html', {'form':form, 'success':success}),
              'success':success}
    return HttpResponse(simplejson.dumps(result))
                                                                                                                              

def search_personal_library(user, search_term):
    #TODO: error check, what if user does not have a ML?
    ml = MediaLibrary.objects.get(user=user) 
    mo = ml.media_object
    if search_term == "":
        return mo.filter(original=False).filter(format__label='png').order_by('-id')
   
    #TODO: need to write code for search term
    return []

from django.http import HttpResponseServerError

def personal_library_search(request):
    # user must be logged in to use
    user = request.user
    if not user.is_authenticated():
        msg = simplejson.dumps('Error: User not logged in')
        return HttpResponseServerError(msg, mimetype='application/json')
    if request.is_ajax():
        # get images from personal library
        if "SEARCH_PAGE_CHANGE" in request.GET:
            page_number = request.GET['PAGE_NUMBER'] 
            #TODO: account for search terms
            search_term = '' #request.GET['SEARCH_TERM']
            objs = search_personal_library(user, search_term)
            NUM_ITEMS_PER_PAGE = 35
            paginator = Paginator(objs, NUM_ITEMS_PER_PAGE)
            try:
                objs = paginator.page(page_number).object_list
            except PageNotAnInteger:
                objs = paginator.page(1).object_list
            except EmptyPage:
                objs = paginator.page(paginator.num_pages).object_list
            
            for obj in objs:
                obj.all_tags = simplejson.dumps([tag.name for tag in obj.tags.all()])
                        
            obj_json = serializers.serialize('json', objs, extras=('all_tags', ))
            rtn = {} 
            rtn['num_pages'] = paginator.num_pages
            rtn['media_objects'] = obj_json

            return HttpResponse(simplejson.dumps(rtn))
        elif "TOTAL_NUMBER_OF_PAGES" in request.GET: 
            search_term = ''
            objs = search_personal_library(user, search_term)
            NUM_ITEMS_PER_PAGE = 35
            paginator = Paginator(objs, NUM_ITEMS_PER_PAGE)
            return HttpResponse(simplejson.dumps(paginator.num_pages))
        elif "DELETE_MEDIAOBJECT_FROM_PERSONAL_LIBRARY" in request.GET: 
            moid = request.GET['MEDIAOBJECT_ID']
            ml = MediaLibrary.objects.get(user=user)
            mo = ml.media_object.get(id=moid)
            ml.media_object.remove(mo)
            return HttpResponse(simplejson.dumps('deleted MediaObject'))

        msg = simplejson.dumps('Error: No POST data sent')
        return HttpResponseServerError(msg, mimetype='application/json')

