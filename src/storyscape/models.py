from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.conf import settings

import tagging

from medialibrary.models import MediaObject

DEFAULT_STORY_GENRE = "Children"

# Create your models here.
max_length_bytes = 16384
class Story(models.Model):
    # users represent all users who have added story to their 
    # personal library
    users = models.ManyToManyField(User)
    # NOTE: the author is also in users. 
    creator_uid = models.IntegerField()
    # creator is same as author
    creator_name = models.CharField(max_length=200)
    is_published = models.BooleanField(default=False,blank=True)
    
    is_public = models.BooleanField(default=True,blank=True)
    
    # TODO: should have creation_date and pub_date. The
    # creation date indicates when it was first created 
    # and pub_date is when it is shared, published to 
    # the community
    creation_datetime = models.DateTimeField(auto_now_add=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    description = models.CharField(max_length=max_length_bytes)
    
    url = models.CharField(max_length=255, blank=True, null=True, unique=True)
    download_url = models.CharField(max_length=255, blank=True, null=True, unique=True)
    thumb_url = models.CharField(max_length=255, blank=True, null=True, unique=True)
    #NOTE: this is registered with tags

    #remixes = models.ManyToMany('self', blank=True, null=True)
    #original = models.BooleanField(default=True)
    #published = models.BooleanField(default=False)
    
    ''' TODO:
        override delete, should delete pages and pagemediaobject
        on story delete
    '''

    def __unicode__(self):
        try: 
            msg = "Title- " + self.title + ": Author- " + self.creator_name
        except ObjectDoesNotExist: 
            msg = "Story, not populated yet"

        return msg

    def get_zip_name(self):
        story_name = self.title.replace(" ", "_")
        return story_name+'.zip'

    def get_thumbnail_name(self):
        return 'thumbnail_icon.png'
    
    def get_filesave_path(self):
        story_name = self.title.replace(" ", "_")
        story_zip_name = self.get_zip_name()
        rurl = settings.SITE_URL+settings.MEDIA_URL+settings.STORYSCAPE_STORIES_URL_ROOT
        story_thumbnail_name = self.get_thumbnail_name()
        creator = User.objects.get(id=self.creator_uid)
        
        self.download_url = rurl+creator.username+'/'+story_name+'/'+story_zip_name
        rurl = settings.STORYSCAPE_STORIES_URL_ROOT
        self.thumb_url = rurl+creator.username+'/'+story_name+'/'+story_thumbnail_name
        file_save_path = settings.STORYSCAPE_IMAGE_URL_ROOT + self.creator_name +'/' + story_name + '/' 
        return file_save_path

class Page(models.Model):
    # each page is associated with a particular Story
    story = models.ForeignKey(Story)
    page_number = models.IntegerField()
    #media_objects = models.ManyToManyField(PageMediaObject)

    def __unicode__(self):
        try: 
            msg = "Page- " + str(self.page_number) + ": Story- " + self.story.title
        except ObjectDoesNotExist: 
            msg = "Page , not populated yet"

        return msg


'''
PageMediaObject wraps a MediaObject associating specific meta
data that should be used with the particular MediaObject.  
'''
class PageMediaObject(models.Model):
    # MediaObjects will contain url, if null means pmo is text
    media_object = models.ForeignKey(MediaObject, null=True)
    page = models.ForeignKey(Page)
    # a media object may be dimensionless, so don't require
    # that type of information. Ex: an audio file.
    xcoor = models.IntegerField(default=0)
    ycoor = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    z_index = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    anime_code = models.IntegerField(default=-1)
    # make sure values consistent accross platforms 
    animate_on = models.IntegerField(default=0) 
    goto_page = models.IntegerField(default=-1) 
    trigger_reaction_on = models.IntegerField(default=0) 
    #should default to none on reaction_object but django-south not 
    #picking up diff, chanage later (7/4/13)
    reaction_object = models.CharField(max_length=255, 
                                blank=True, null=True)  
    assoc_text = models.CharField(max_length=max_length_bytes, 
                                blank=True, null=True)  

    ''' WORKING on integrating text page media objects. 
        Need to consider assoc_text with images and ability
        to add it via builder UI.
    '''
    media_type = models.CharField(max_length=5, blank=True, null=True, 
                                  default='image')  
    # if type text there is associated font info
    font_style = models.CharField(max_length=60, blank=True, 
                                  null=True, default="sans_serif")
    font_size  = models.IntegerField(blank=True, null=True, default=48)
    font_color = models.CharField(max_length=10, blank=True, 
                                  null=True, default="#000000")

    # In some cases a copy/modification of the original content
    # will be created for use on a mobile platform, this should be
    # the location of the content you want to be used for download
    download_media_url = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    def natural_key(self):
        return (self.media_object.url)
        #NOTE: this could be buggy, what if media_object does not exist?
    
    

    def __unicode__(self):
        try:
            if self.media_object != None: 
                msg = "url- "+self.media_object.url+": page- " 
            else:
                msg = "url- text media object "
            msg = msg + str(self.page.page_number) + ": story- " + self.page.story.title
        except ObjectDoesNotExist: 
            msg = "PageMediaObject, not populated yet"

        return msg

class StoryLibrary(models.Model):
    """
    StoryLibrary is meant to be a personal subset of all story objects. 
    These are the story items that a user wants to keep in their own 
    library for easy access, and can be either published or unpublished. 
    """
    user = models.ForeignKey(User)
    stories = models.ManyToManyField(Story)
    
try: 
    tagging.register(Story)
except tagging.AlreadyRegistered:
    pass

class StoryDownload(models.Model):
    '''
    used to track story downloads, for metrics and whatnot
    '''
    story = models.ForeignKey(Story)
    user = models.ForeignKey(User, null=True)
    device_id = models.CharField(max_length=20)
    download_time = models.DateTimeField(auto_now_add = True)