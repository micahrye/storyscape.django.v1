"""
Design of this model is influnced by Dublin Core Element Set Metadata. 
"""

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import tagging
from tagging.fields import TagField

from django.forms import ModelForm


# registered with tagging, decleration near end of file.

MEDIAOBJECT_max_length_bytes = 16384
MEDIAOBJECT_max_length_name = 60

def upload_file_to(instance, filename):
    # this way we spread out where images saved, but always in the 
    # same dir for a user
    # note instance is a User object see view where instance set from request.user
    ftype = filename[-3:].lower()
    filename = filename[:-3] + ftype
    path = settings.MEDIAOBJECT_UPLOAD_URL_ROOT_DIR_NAME +'/org/' + ftype + '/' 
    
    #IMPORTANT: what to know the file type since we sort into different dirs ... 
    
    path += instance.creator.username + '/'
    # instance.user.date_joined.strftime('%Y/%m/%d/')
    path +=  filename
    
    return path


class MediaType(models.Model):
    """
    simple model used to indicate if media is a still image, video, 
    audio, or other type of media. 

    See http://dublincore.org/documents/dcmi-type-vocabulary/ for info 
    on types, part of dublin core metadata 
    """ 
    label = models.CharField(max_length=20, default='unknown')
    """TODO: need to add description """

class MediaFormat(models.Model):
    """
    simple model used to indicate if media is a still image, video, 
    audio, or other type of media 'StillImage' ...
    """ 
    label = models.CharField(max_length=10, default='unknown')
    """TODO: need to add description """

class MediaObject(models.Model):
    """
    MediaObject is used to model image, video, and audio types of 
    media
    """ 
    name = models.CharField(max_length=MEDIAOBJECT_max_length_name, blank=True, default='imagefile') 
    # CURRENTLY this is the modified url? should be the original??????
    url = models.CharField(max_length=255, unique=True, blank=True)
    """
    create a recursive relationship--an object that has a many-to-many
    relationship with objects of the same model class. 
    """
    related = models.ManyToManyField('self', blank=True)
    
    """ 
    I think it is less memory and faster to reference the 
    foreign key, rather than have these be char fields. 
    """
    """
    NOTE: should allow type and format to be null, this way you can 
    use get_or_create with MediaObject
    """
    type = models.ForeignKey(MediaType, blank=True)
    format = models.ForeignKey(MediaFormat, blank=True)
    publisher = models.CharField(max_length=60, default="Sodiioo", blank=True)
    license = models.CharField(max_length=60, blank=True,
                          default='http://web.resource.org/cc/PublicDomain')
     
    creator = models.ForeignKey(User, null=True, blank=True)
    creation_datetime = models.DateTimeField('date time of creation')

    original = models.BooleanField(default=False)
    # used for form for uploading image 
    upload_image = models.ImageField(upload_to=upload_file_to,
                                       max_length=60, blank=False, null=True)
    #tags, this model is registered below with django-tagging
    has_tag = models.IntegerField(blank=True, null=True, default=0)
    mo_tags = TagField(verbose_name = "Image Tags")

class MediaLibrary(models.Model):
    """
    MediaLibrary is meant to be a personal subset of all media objects. 
    These are the media items that a user wants to keep in their own 
    library for easy access. 
    """
    user = models.ForeignKey(User)
    media_object = models.ManyToManyField(MediaObject)



class ImageObject(models.Model):
    image = models.ImageField(upload_to=upload_file_to,
                              max_length=60, blank=False, null=True)
'''
TODO: need to change this name here and in ImageUploadForm2, 
also need to change that name, get rid of 2
'''
class ImageObject2(models.Model):
    user = models.ForeignKey(User)
    image = models.ImageField(upload_to=upload_file_to,
                              max_length=60, blank=False, null=True)


class ImageUploadForm2(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ImageUploadForm2, self).__init__(*args, **kwargs)
        # change display label for form item 'name' 
        
    class Meta:
        model = MediaObject
        fields = ('upload_image', 'mo_tags', )

    def save(self, *args, **kwargs):
        
        # the image gets saved to the MEDIA_ROOT + path defined in upload_to here
        imgobjectform = super(ImageUploadForm2, self).save(*args, **kwargs)
        imgobjectform.url = imgobjectform.upload_image.name
        '''
        mod_url = org_url = settings.MEDIALIBRARY_URL_ROOT + imgobjectform.url
        ftype = mod_url[-3:]
        # create url for modified image. All images should have a png modified copy for use
        mod_url = mod_url.replace('/org/', '/mod/')
        if ftype != 'png':
            mod_url = mod_url.replace('/'+ftype+'/', '/png/')
            mod_url =  mod_url[:-3] + 'png'
        
        # create a modification of the original image that was uploaded. 
        # recall that svg files not handled by ImageField.
        results = commands.getoutput('mkdir -p ' + os.path.split(mod_url)[0]) 
        if (imgobjectform.upload_image.height > 300) or (imgobjectform.upload_image.width > 300): 
            cmd = 'convert -resize 300x300 ' + org_url + ' ' + mod_url
            results = commands.getoutput(cmd)
        else: 
            cmd = 'convert '  + org_url + ' ' + mod_url
            results = commands.getoutput(cmd)
        '''
        return imgobjectform
'''
class ImageUploadForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        # change display label for form item 'name' 
        
    class Meta:
        model = ImageObject2
        exclude = ('user', )

    def save(self, *args, **kwargs):
        user = self.instance
        upload_image = self.cleaned_data.get('image')
        
        # the image gets saved to the MEDIA_ROOT + path defined in upload_to here
        imgobjectform = super(ImageUploadForm, self).save(*args, **kwargs)
'''      
            

try:
    tagging.register(MediaObject)
except tagging.AlreadyRegistered:
    pass

import signals
signals.MediaLibrary # just here to silence warnings