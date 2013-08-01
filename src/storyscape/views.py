import commands
import os
import random
import logging 
from collections import OrderedDict

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt

from django.db.models.query import QuerySet
from django.utils.html import strip_tags

from django.core import serializers
from django.db import IntegrityError
from itertools import chain
import settings
import simplejson

from tagging.models import Tag, TaggedItem

from storyscape.models import Story, PageMediaObject, Page
from django.contrib.auth.models import User
from storyscape import utilities
from medialibrary.models import MediaLibrary, MediaObject

logger = logging.getLogger(__name__)
NUM_ITEMS_PER_PAGE = 40
NUM_TAGS_PER_PAGE = 20

ACTION_TRIGGER_CODES = OrderedDict([('Touch', 300),
                        ('Sound', 301),
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

def addPageMediaObjects(page, json_mediaobjects):
    for obj in json_mediaobjects:
        if obj['type'] == 'image':
            
            try:
                obj_id = obj['mo_id']
            except KeyError:
                return {'errors':['Error adding mediaobject '+obj['name']+' to page, mediaobject id DNE']}
            # media object should always alread exist
            mo = MediaObject.objects.get(id=obj_id)
            # page media object may not exist
            try: 
                pmo_id = int(obj['pmo_id'])
                if pmo_id == -1:
                    pmo = PageMediaObject(media_object=mo, page=page)
                else:
                    pmo = PageMediaObject.objects.get_or_create(id=pmo_id, media_object=mo, page=page)[0]
            except (KeyError, IntegrityError):
                pmo = PageMediaObject(media_object=mo, page=page)
        elif obj['type'] == 'text': #Images should always already exist as a mediaobject, text media will not
            try: 
                pmo_id = int(obj['pmo_id'])
                if pmo_id == -1:
                    pmo = PageMediaObject(media_object=None, page=page)
                else:
                    pmo = PageMediaObject.objects.get_or_create(id=pmo_id, media_object=None, page=page)[0]
            except (KeyError, IntegrityError):
                pmo = PageMediaObject(media_object=None, page=page)
            
            # recall default font style is SERIF
            pmo.font_style = obj['font_style'] if obj['font_style'] != '' else pmo.font_style
            pmo.font_size = obj['font_size']
            # default color #000000
            pmo.font_color = obj['font_color'] if len(obj['font_color']) >= 7 else pmo.font_color

        pmo.anime_code = obj['anime_code']
        pmo.animate_on = obj['animate_on']
        pmo.goto_page = obj['goto_page'] 
        pmo.trigger_reaction_on = obj['trigger_reaction_on'] 
        pmo.reaction_object = obj['reaction_object'] 
        pmo.xcoor = obj['xcoor']
        pmo.ycoor = obj['ycoor']
        pmo.z_index = obj['z_index']
        pmo.width = obj['width']
        pmo.height = obj['height']
        pmo.assoc_text = obj['text'] 
        pmo.media_type = obj['type']
        pmo.save()
    
    return {'success': ['all objects added to page']}

def story_objects_to_json(story_objects):
    stories_list = []
    tmp = {} 
    # if sinble story object passed in, not a list, then make it into a list
    if not story_objects.__class__ == list and not story_objects.__class__ == QuerySet:
        story_objects = [story_objects]
    
    for story in story_objects: 
        tmp["story_id"] = story.id
        tmp["title"] = story.title
        tmp["creator_uid"] = story.creator_uid #? correct that dataitem creator created the contained data?
        tmp["author_name"] = story.creator_name
        tmp["genre"] = story.genre
        tmp["description"] = story.description
        tmp["tags"] = [tag.name for tag in story.tags]
        tmp["num_pages"] = story.page_set.count()
        stories_list.append(tmp)
        tmp = {}
    return simplejson.dumps(stories_list)

def page_objects_to_json(page_objects):
    page_list = []
    tmp = {} 
    # if single story object passed in, not a list, then make it into a list
    if not page_objects.__class__ == list and not page_objects.__class__ == QuerySet:
        page_objects = [page_objects]
    
    #TODO: the order of the pages matters, we want to make sure that we go from 
    # page 1 to page N. Currently passing in ordered pages.

    for page in page_objects:
        tmp["page_number"] = page.page_number
        tmp["media_objects_json"] = serializers.serialize("json",
                                       page.pagemediaobject_set.order_by('z_index'), 
                                       relations={'media_object'}) 
        page_list.append(tmp)
        tmp = {} 
    
    return simplejson.dumps(page_list)

def search_stories(search_term):

    if search_term == "":
        return Story.objects.filter(is_published=True)
    ''' GET duplicats if chain, need to develop better search at some point'''
    #qt1 = Tag.objects.filter(name=search_term)
    #set1 = TaggedItem.objects.get_union_by_model(Story, qt1).filter(is_published=True)
    
    qt2 = Tag.objects.filter(name__icontains=search_term)
    set2 = TaggedItem.objects.get_union_by_model(Story, qt2).filter(is_published=True)
    # compine the two querysets into one list
    mos = list(chain([], set2))
    return mos

@login_required
def storyscape(request):
    
    user = request.user 
    
    if request.is_ajax():
        if request.method == "GET": 
            if 'STORY_PAGE' in request.GET:
                story_id = request.GET['STORY_ID']
                story = Story.objects.get(id=story_id)
                pages = story.page_set.all().order_by('page_number')
                # should get an array of arrays, each inner array are the pmos. 
                pages_json = page_objects_to_json(pages)
                return HttpResponse(pages_json)
                
            if 'USER_STORIES' in request.GET:
                stories = Story.objects.filter(users=user).filter(creator_uid=user.id).order_by('creation_datetime')    
    
                #stories_json = simplejson.dumps(stories)
                #stories_json = loads(serialize('json', stories))
                stories_json = story_objects_to_json(stories)

                return HttpResponse(stories_json)
            
        if request.method == 'POST':
            if 'STORY_CREATION' in request.POST:
                save_data = request.POST['STORY_CREATION']
                json_data = simplejson.loads(save_data)
                title = json_data['title'].strip()  
                genre = json_data['genre'].strip()
                desc = json_data['description'].strip()
                tags = json_data['tags'].strip()
#NEED: to lowercase all input, maybe
                
                rtn = {} 
                story = Story(creator_uid=user.id, creator_name=user.username, 
                              title=title, genre=genre, description=desc)
                story.save()
                story.users.add(user)
                story.save() # don't think i need this save
                if(len(tags) > 0): 
                    story.tags = tags
                rtn['result'] = 'created'
                rtn['msg'] = 'Story Created'
                
                story_json = story_objects_to_json(story)
                rtn['story_json'] = story_json
                return HttpResponse(simplejson.dumps(rtn))
            elif 'SAVE_PROPS' in request.POST:
                save_data = request.POST['SAVE_PROPS']
                json_data = simplejson.loads(save_data)
                title = json_data['title'].strip()  
                genre = json_data['genre'].strip()
                desc = json_data['description'].strip()
                tags = json_data['tags'].strip()
                story_id = json_data['id']
                
                story = Story.objects.get(id=story_id)
                story.title = title
                story.genre = genre
                story.description = desc
                story.tags.delete()
                story.tags = tags
                story.save()
                return HttpResponse(simplejson.dumps('success'))
                
            elif 'PAGE_SAVE' in request.POST:
# !!! DO we allow stories that have been published to be modified? Or would that become a REMIX  ????? 
# allow and add version/edition? 
                save_data = request.POST['PAGE_SAVE']
                # JSONDecodeError if not json
                json_mediaobjects = simplejson.loads(save_data) #should be list
                obj = json_mediaobjects[0]
                story_id = obj['story_id']
                story = Story.objects.get(id=story_id)
                
                try: 
                    # here we are modifying a story. Since we are modifying the story we will want 
                    page = Page.objects.filter(story=story).get(page_number=obj['page_number'])
                    pmo_ids = []
                    for mo in json_mediaobjects:
                        try:
                            pmo_ids.append(mo['pmo_id'])
                        except KeyError:
                            pass
                    # remove invalid values 
                    pmo_ids = [x for x in pmo_ids if x !='undefined' and x !=-1 and x !='-1']
                    # clear pmo that have been removed from page in ui and hence page
                    [ pmo.delete() for pmo in page.pagemediaobject_set.exclude(id__in=pmo_ids) ]
                    # take json object and add to database
                    result = addPageMediaObjects(page, json_mediaobjects)
                    if 'errors' in result: 
                        msg = result['errors'][0]
                    else: 
                        msg = 'page modified ' + result['success'][0] 
                except Page.DoesNotExist:
                    # create a new page and add page media objects to it 
                    # SW - newly created pages are saved when added now
                    #     to prevent pages from being saved over each other
                    page = Page(story=story)
                    page.page_number = obj['page_number']
                    page.save()
                    
                    result = addPageMediaObjects(page, json_mediaobjects)
                    if 'errors' in result: 
                        msg = result['errors'][0]
                    else: 
                        msg = 'page created ' + result['success'][0] 
                    
                return HttpResponse(msg)
            
            elif 'SHARE_STORY' in request.POST:
                # story and pages should be saved
    # !!! if a story has already been published should any changes to it result in a REMIX !!! ???? 
                msg = 'Trying to share but something went wrong?'
                
                ''' NOTE:
                    for each mediaobject we want to convert any media (svg) to 
                    the correct download type (png)
                    NOTE: this could be a bug area, what if we cannot generate 
                    download type? etc. 
                    NOTE: since multiple stories can use the same media we must save the download media 
                    specific to a story
                '''
                
                ss_path_root = settings.STORYSCAPE_IMAGE_URL_ROOT
                ml_path_root = settings.MEDIALIBRARY_URL_ROOT
                story = Story.objects.get(id=request.POST['SHARE_STORY'])
                pages = story.page_set.order_by('page_number')
                for page in pages:
                    pmos = page.pagemediaobject_set.order_by('z_index')
                    for pmo in pmos: 
                        ''' TODO:
                            each pmo image object should be a png file, we 
                            need to see if there corresponding
                            svg files from which we should make the resized 
                            png for the story download. This 
                            will ensure the highest quality images for the 
                            stories. 
                        '''
                        
                        '''
                            The same media object can be associated 
                            with different pages, need to check if we have 
                            created download media for that object yet, if 
                            so need to change file name to save unique copy. 
                        '''
                        ''' IMPORTANT
                            we display png (jpg?) files in UI because not all 
                            browsers handle svg well. But
                            there may (may not) be a corresponding svg. What 
                            about JPG ... got to think about this 
                        '''
                        ''' IMPORTANT
                            not always using original image, new images are getting pulled
                            from mod, not original, still need to account for original of 
                            type jpg
                        '''
                        if pmo.media_type == 'image':
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
                            
                            dload_url = story.creator_name+'/'
                            dload_url += story.title.replace(" ", "_")
                            #if there is a svg file to use for image resize/creation use it 
                            if url[len(url)-3:].lower() == 'svg':          
                                dload_url += "/" + os.path.split(url)[1][:-3]+'png'
                            elif url[len(url)-3:].lower() == 'jpg': 
                                dload_url += "/" + os.path.split(url)[1][:-3]+'png'
                            else:
                                dload_url += "/" + os.path.split(url)[1]
                                
                            # if the file already exists we want to create a different named file
                            for _ in range(0,10):
                                if os.path.exists(ss_path_root+dload_url):
                                    dload_url = dload_url[:-4]+"_"+str(random.randint(0,100000))+".png"
                                else: 
                                    break
                                        
                            #if dir DNE create it
                            if not os.path.exists(os.path.split(ss_path_root + dload_url)[0]): 
                                os.makedirs(os.path.split(ss_path_root + dload_url)[0])  
                            ''' Imagemagick settings 
                                -background: background color
                            
                            '''
                            # convert -background none -resize 800x200\! railroad.svg +antialias railroad.png
                            cmd_str = 'convert -background none '+ ml_path_root+ url +' -resize '
                            cmd_str += str(pmo.width) +'x'+ str(pmo.height)+'\! +antialias png32:'+ ss_path_root+dload_url
                            results = commands.getoutput(cmd_str)
                            if not results: 
                                pmo.download_media_url = dload_url
                                pmo.save()
                                msg = 'seems to have went well'
                            elif (pmo.width == 0) or (pmo.height == 0): 
                                pmo.delete() 
                            else:
                                msg = "download_media_url not created"
                                return HttpResponse(msg)
                        else:
                            pass
                        
                        
                story.is_published = True 
                story_name = story.title.replace(" ", "_")
                story_zip_name = story_name+'.zip'
                story_thumbnail_name = 'thumbnail_icon.png'
                #TODO not sure that using /media/... is best might want root url to be anything 
                # after system media storage since technically that name "media" can be different
                # but stories will always be in the media dir, regardless of its name
                rurl = settings.SODIIOO_SITE_URL+settings.MEDIA_URL+settings.STORYSCAPE_STORIES_URL_ROOT
                #NOTE: download urls are relative to website while all other urls are 
                # relative to project
                story.download_url = rurl+user.username+'/'+story_name+'/'+story_zip_name
                rurl = settings.STORYSCAPE_STORIES_URL_ROOT
                story.thumb_url = rurl+user.username+'/'+story_name+'/'+story_thumbnail_name
                story.save()
                # NOTE: story titles can only use alpha-numeric characters 
                file_save_path = ss_path_root + story.creator_name +'/' + story_name + '/' 
                try: 
                    utilities.story_to_xml(story, file_save_path)
                except IOError:
                    msg = 'error creating xml version of story'
                    
                utilities.create_story_nomedia_file(file_save_path)
                # TODO: IMPORTANT
                # need to create a thumb for the story use convert to create tha
                if not utilities.create_story_thumbnail(story, file_save_path):
                    msg = 'error creating thumbnail'
                
                if not utilities.create_story_zip(story, file_save_path):
                    msg = 'error creating downloadable media'
                
                exempt = [story_thumbnail_name, story_zip_name]  
                utilities.remove_dir_files(file_save_path, exempt) 
                # IMPORTANT: need to add logging of error at some point !!
                # IMPORTANT: 
                # TODO: 
                # need to add code to create zip file, want some strcure like 
                # StoryName/
                # - storyname.zip  (contains all media and thumbnail for story)
                # - thumbnail.png
                return HttpResponse(msg)
            elif 'DELETE_STORY' in request.POST:
                story_id = request.POST['DELETE_STORY']
                story = Story.objects.get(id=story_id)
                story.delete()
                msg = 'Story with id = ' + story_id + ' has been deleted'
                return HttpResponse(simplejson.dumps(msg))

            elif 'DELETE_PAGE' in request.POST: 
                story_id = request.POST['STORY_ID']
                page_number = int(request.POST['DELETE_PAGE'])
                story = Story.objects.get(id=story_id)
                pages = story.page_set.all().order_by('page_number')
                page = pages[page_number]
                '''TODO: if there has been downloadable media created 
                   #for this page need to remove that also
                '''
                page.delete()
                for page in pages[ (page_number): ]:
                    page.page_number = page.page_number - 1
                    page.save()

                msg = 'Page ' + str(page_number) + ' deleted and story updated'
                return HttpResponse(simplejson.dumps(msg))
            elif 'NEW_PAGE' in request.POST:
                story_id = request.POST['STORY_ID']
                page_number = int(request.POST['NEW_PAGE'])
                story = Story.objects.get(id=story_id)
                pages = story.page_set.all().order_by('page_number')
                for page in pages[page_number:len(pages)]:
                    page.page_number += 1
                    page.save()
                new_page = Page(story=story)
                new_page.page_number = page_number
                new_page.save()
                msg = 'no error'
                # jQuery 1.9.1 more strict, if you tell its ajax that you expect JSON back
                # you need to send JSON back or error
                return HttpResponse(simplejson.dumps(msg))

    stories = Story.objects.filter(users=user).filter(creator_uid=user.id).order_by('-creation_datetime')    
    # IMPORTANT: 
    # BUG:
    # if user does not have a MediaLibrary it throws an error
    ml = MediaLibrary.objects.get(user=user)
    # IMPORTANT !! need to account for different image types !!!
    from django.db.models import Q
    media_objects = ml.media_object.filter(Q(format__label='png') | Q(format__label='jpg')).order_by('-id')[:NUM_ITEMS_PER_PAGE]
    
    return render_to_response(
                 'storyscape/create.html',
                 {'user': request.user, 
                  'show_personal_library': True,
                  "media_objects": media_objects,
                  "stories":stories,
                  'action_codes':ACTION_CODES,
                  'action_trigger_codes':ACTION_TRIGGER_CODES},
                 context_instance=RequestContext(request))


@csrf_exempt
def search_index(request):
    if request.is_ajax():
        if request.method == "GET":
            if("TEXT_SEARCH" in request.GET or "TAG_SEARCH" in 
               request.GET or "SEARCH_PAGE_CHANGE" in request.GET ):
               
                page_number = request.GET.get('PAGE_NUMBER', -1)
                search_term = request.GET['SEARCH_TERM']
                
                stories = search_stories(search_term)
                paginator = Paginator(stories, NUM_ITEMS_PER_PAGE)
                try:
                    stories = paginator.page(page_number).object_list
                except PageNotAnInteger:
                    stories = paginator.page(1).object_list
                except EmptyPage:
                    stories = paginator.page(paginator.num_pages).object_list
                
                # want to serialize objects to json
                # TO be able to send back the tags via json to UI
                for s in stories:
                    s.all_tags = simplejson.dumps([tag.name for tag in s.tags.all()])
                   
                so_json = serializers.serialize('json', stories, extras=('all_tags', ))
                #rt_json = serialize_tags(random_tags)
                rtn = {}
                rtn['num_pages'] = paginator.num_pages
                rtn['stories'] = so_json
                #rtn['random_tags'] = rt_json
                return HttpResponse(simplejson.dumps(rtn))
                
            

#TODO: IMPORTANT need to have dynamic list of stories 
# that are published to send to mobile story search... 
def personalStoryLib(request, username):
    #TODO: change, currently getting all published stories, that should be its
    #its own view
    user = get_object_or_404(User, username=username)
    stories = Story.objects.filter(creator_uid=user.id)
    root_url = 'http://sodiioo.media.mit.edu/media/storyscape_media/stories/'
    if request.method == 'GET':
        if 'BASIC_SEARCH' in request.GET:
            #TODO: need to implement all the search stuff
            msg = '' 
            published = Story.objects.filter(is_published=True)
            for story in published:
                title = story.title.replace(' ', '_')
                url = root_url + story.creator_name +'/'+title+'/'+title+'.zip'
                msg = msg + url + ', '
            msg = msg[:-2]
            return HttpResponse(msg)

    return render_to_response('storyscape/myStories.html', 
        {'username':username, 'stories':stories}, 
        context_instance=RequestContext(request))
    

def storyscapeBookInfo(request, username):
    """
    This view has not been implmented, only a code-node right now. 
    Idea is that this view would give the user info about a selected 
    story. 
    """
    testJSON = [{'happy': [1,3,5,7], 
                'text': 'thats all folks', 'retweeted': False, 
                'dev_note': 'this VIEW is not implemented yet'}]
    rtn = simplejson.dumps(testJSON)
    return HttpResponse(rtn)



def stories_library(request):
    
    if not request.user.is_authenticated():
        return render_to_response('public/index.html',context_instance=RequestContext(request))
    
    objs = []
    if request.is_ajax():
        if request.method == "GET":
            if "TOTAL_NUM_PAGES" in request.GET: 
                objs = Story.objects.filter(is_published=True)
                paginator = Paginator(objs, NUM_ITEMS_PER_PAGE) 
                return HttpResponse(simplejson.dumps(paginator.num_pages))
            
            if( "TEXT_SEARCH" in request.GET or 'TAG_SEARCH' in
                request.GET or 'SEARCH_PAGE_CHANGE' in request.GET ):
                
                page_number = request.GET.get('PAGE_NUMBER', 1)
                search_term = request.GET['SEARCH_TERM']
                ''' IMPORTANT: 
                need to consider non-alphanumeric characters, need to consider
                code injection vulnerablity 
                '''
                objs = search_stories(search_term)
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
                #rt_json = serialize_tags(random_tags)
                rtn = {}
                rtn['num_pages'] = paginator.num_pages
                #instead of passing as rtn['stories'] and rtn['media_objects'] separately
                #we can pass it as one parameter as rtn['objs'] but for now, I don't want
                #to change the html files
                rtn['stories'] = obj_json
                
                return HttpResponse(simplejson.dumps(rtn))
            
        
    objs = Story.objects.filter(is_published=True)
    paginator = Paginator(objs, NUM_ITEMS_PER_PAGE)
    try:
        objs = paginator.page(1).object_list
    except EmptyPage:
        pass

    # we get the most common tags for this type of media object
    #all_tags, most_common_tags = get_most_common_tags(num_tags_rtn)
    most_common_tags = []
    # we get a random sample of tags for this media object
    #random_tags = get_random_tags(all_tags, NUM_TAGS_PER_PAGE)
    random_tags = ''  
    
    print request.user.is_authenticated()
    return render_to_response('storyscape/stories_library.html', 
                              {'user':request.user, 'stories':objs, 
                              'most_common_tags': most_common_tags, 
                              'random_tags': random_tags}, 
                              context_instance=RequestContext(request))


def is_int(num):
    try: 
        int(num)
        return True
    except ValueError: 
        return False 

@csrf_exempt
def get_story(request, username):
    
    if request.method == 'GET':
        if 'SODIIO_REQUEST' in request.GET:
            url_root = settings.MEDIA_URL
        else: 
            url_root = settings.SODIIOO_SITE_URL + settings.MEDIA_URL
        if 'STORY_ID' in request.GET:
            sid = strip_tags(request.GET.get('STORY_ID', -1))
            if sid == -1 or not is_int(sid) :
                return HttpResponse(simplejson.dumps('invalid id argument'))
            try: 
                s = Story.objects.filter(is_published=True).get(id=sid)
            except Story.DoesNotExist: 
                return HttpResponse(simplejson.dumps('invalid argument'))
            num_pages = s.page_set.all().count()
            rtn_story = {'title':s.title, 
                          'author':s.creator_name, 
                          'num_pages':num_pages, 'pages':[]}
            pages = s.page_set.order_by('page_number')
            for i, page in enumerate( pages ): 
                rtn_story['pages'].append([])
                for pmo in page.pagemediaobject_set.order_by('z_index'): 
                    # get all the pmo objects and add to current page
                    try: 
                        url = url_root + pmo.media_object.url
                    except( TypeError, AttributeError ): 
                        url = ''
                    if pmo.media_type == 'text':
                        font_size = pmo.font_size
                        font_style = pmo.font_style
                        font_color = pmo.font_color
                    else: 
                        font_size = font_style = font_color = '' 
                    rtn_pmo = {'type':pmo.media_type, 'x':pmo.xcoor, 'y':pmo.ycoor,
                               'width': pmo.width, 'height':pmo.height, 'text':pmo.assoc_text, 
                               'font_size': font_size, 'font_style':font_style, 
                               'font_color':font_color,
                               'url': url} 
                    rtn_story['pages'][i].append(rtn_pmo)
                
            return HttpResponse(simplejson.dumps(rtn_story))
        
        if 'STORIES' in request.GET: 
            stories = Story.objects.filter(is_published=True)
            rtn_stories = []
            for story in stories: 
                rtn_stories.append({'title':story.title, 
                                    'id': story.id})

            return HttpResponse(simplejson.dumps(rtn_stories))

    return HttpResponse(simplejson.dumps('invalid arguments'))


def reader_info(request):
    return render_to_response('storyscape/about_reader.html', 
                              {}, 
                              context_instance=RequestContext(request))

def story_preview(request, story_id):    
    return render_to_response( request, 'story_preview.html', dict(story_id=story_id), context_instance=RequestContext(request) )
