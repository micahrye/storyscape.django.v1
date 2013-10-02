"""
Design of this model is influnced by Dublin Core Element Set Metadata. 
"""

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import tagging, os
from tagging.fields import TagField

from django.forms import ModelForm, BooleanField, ValidationError


# registered with tagging, decleration near end of file.

MEDIAOBJECT_max_length_bytes = 16384
MEDIAOBJECT_max_length_name = 60

DEFAULT_LICENSE = 'http://web.resource.org/cc/PublicDomain'

def upload_file_to(instance, filename):
    # this way we spread out where images saved, but always in the 
    # same dir for a user
    # note instance is a User object see view where instance set from request.user
    filename_base, ext = os.path.splitext(filename)
    ftype = ext[1:].lower()
    filename = filename_base + "." + ftype
    path = settings.MEDIAOBJECT_UPLOAD_URL_ROOT_DIR_NAME +'/org/' + ftype + '/' 
    
    #IMPORTANT: what to know the file type since we sort into different dirs ... 
    
    path += instance.creator.username + '/'
    # instance.user.date_joined.strftime('%Y/%m/%d/')
    path +=  filename.replace(" ","_")
    
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
                          default=DEFAULT_LICENSE)
     
    creator = models.ForeignKey(User, null=True, blank=True)
    creation_datetime = models.DateTimeField('date time of creation')

    original = models.BooleanField(default=False)
    # used for form for uploading image 
    upload_image = models.ImageField(upload_to=upload_file_to,
                                       max_length=128, blank=False, null=True)
    #tags, this model is registered below with django-tagging
    has_tag = models.IntegerField(blank=True, null=True, default=0)
    mo_tags = TagField(verbose_name = "Image Tags")
    
    def is_visible(self):
        return not self.license

class MediaLibrary(models.Model):
    """
    MediaLibrary is meant to be a personal subset of all media objects. 
    These are the media items that a user wants to keep in their own 
    library for easy access. 
    """
    user = models.ForeignKey(User)
    media_object = models.ManyToManyField(MediaObject)

class ImageUploadForm(ModelForm):
    
    is_public = BooleanField(label = "Public", required = False, initial = True)
    
    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        # change display label for form item 'name' 
        
    class Meta:
        model = MediaObject
        fields = ('upload_image', 'mo_tags')

    def save(self, *args, **kwargs):
        
        # the image gets saved to the MEDIA_ROOT + path defined in upload_to here
        imgobjectform = super(ImageUploadForm, self).save(*args, **kwargs)
        imgobjectform.url = imgobjectform.upload_image.name

        return imgobjectform
    
    def clean_upload_image(self):
        upload_image = self.cleaned_data.get('upload_image', False)
        if not self.instance.upload_image == upload_image:
            if not any([upload_image.name.lower().endswith(ext) for ext in settings.VALID_EXTENSIONS]):
                raise ValidationError(u'We only accept PNGs and JPEGs at the moment')
        return upload_image
            

try:
    tagging.register(MediaObject)
except tagging.AlreadyRegistered:
    pass

import signals
signals.MediaLibrary # just here to silence warnings