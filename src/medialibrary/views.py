import datetime
import os
import commands, random, string

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from decorators import ajax_required
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings

import simplejson

from tagging.models import TaggedItem, Tag

from medialibrary.models import MediaLibrary, MediaObject, ImageUploadForm, MediaFormat, MEDIAOBJECT_max_length_name, MediaType, DEFAULT_LICENSE

NUM_ITEMS_PER_PAGE = 15
NUM_TAGS_PER_PAGE = 50


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

@ajax_required
@login_required
@require_POST
def toggle_media_object_visibility(request):
    user = request.user
    mo_id = request.POST['MEDIA_OBJECT_ID']
    
    mo = MediaObject.objects.get(id=mo_id, creator=user)
    
    if mo.is_visible():
        mo.license = DEFAULT_LICENSE
        is_visible = False
    else:
        mo.license = ""
        is_visible = True
    mo.save()
    
    return HttpResponse(simplejson.dumps(dict(is_visible = is_visible)))


def index(request):
    return render_to_response('medialibrary/media_index.html', 
                              dict(), 
                              context_instance=RequestContext(request))

@ajax_required
@require_GET
def get_media_objects(request):
    page_number = int(request.GET.get('PAGE_NUMBER', 1))
    search_term = request.GET.get('SEARCH_TERM', '')
    get_all_images = request.GET.get('GET_ALL', 'true') == 'true'
    get_favorites = request.GET.get('GET_FAVORITES', 'true') == 'true'
    need_add_buttons = request.GET.get('NEED_ADD_BUTTONS', 'true') == 'true'
    
    if search_term:
        tag_query = Tag.objects.filter(name__icontains=search_term)
        query = TaggedItem.objects.get_union_by_model(MediaObject, tag_query)
    else:
        query = MediaObject.objects

    library = None
    if get_favorites:
        library = MediaLibrary.objects.get(user=request.user)
        favorite_ids = library.media_object.values_list('id', flat=True)
        query = query.filter(id__in = favorite_ids)
    elif not get_all_images:
        query = query.filter(creator = request.user)
    else:
        query = query.exclude(license = "")
        
    query = query.filter(original=False).filter(format__label='png').order_by('-id') 
    objs = query.all()
    
    paginator = Paginator(objs, NUM_ITEMS_PER_PAGE)
    
    page_number = min(paginator.num_pages, page_number)
    objs = paginator.page(page_number).object_list
    
    favorited_ids = []
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


def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@login_required
@ajax_required
def image_upload(request):
    
    user = request.user
    form = ImageUploadForm()
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
        form = ImageUploadForm(request.POST, request.FILES, instance=mo)
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
            # mo.url gets set inside form.save(), this way we ensure that the 
            # url name is unique sice django takes care of the user uploading files
            # with the same file name by appending an int
            form.save()
            mo.original = True
            tags = request.POST['mo_tags'].lower()
            mo.tags = tags
            mo.has_tag = 1
            
            if not form.cleaned_data['is_public']:
                mo.license = ""
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
            
            mod_url = mod_url.replace(settings.MEDIALIBRARY_URL_ROOT, '')
            i = 0
            while i < 10 and MediaObject.objects.filter(url = mod_url).count():
                mod_url = mod_url[:-4] + generate_id() + mod_url[-4:]
            
            cmd = 'convert -resize 300x300 ' + org_url + ' ' + settings.MEDIALIBRARY_URL_ROOT + mod_url
            _ = commands.getoutput(cmd)
            
            mod_mo.url = mod_url
            
            
            if not form.cleaned_data['is_public']:
                mod_mo.license = ""
            
            mod_mo.save()
            mod_mo.tags = tags
            # add modified image to personal library 
            ml.media_object.add(mod_mo)
            success = True
            form = ImageUploadForm()

    result = {'form':render_to_string('medialibrary/image_upload.html', {'form':form, 'success':success}),
              'success':success}
    return HttpResponse(simplejson.dumps(result))

