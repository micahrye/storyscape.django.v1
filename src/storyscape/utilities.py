import commands, logging, random
import os, StringIO

from storyscape.models import Story, PageMediaObject, MediaObject
from django.conf import settings

from unidecode import unidecode

''' Utility methods used by storyscape. 
    Developer: Micah Eckhardt
    Creation date: 08-21-12
'''

STORY_THUMBNAIL_SIZE = 180

def create_download_media(pmo, story):
    dload_url = story.creator_name+u'/'
    dload_url += story.title.replace(" ", "_") + u'/'
    dload_url = unidecode(dload_url)
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
    result = commands.getoutput(cmd_str)
    if result:
        logging.error("Error with pmo {0}\n{1}\n\n{2}".format(pmo.id, cmd_str, result))
    pmo.download_media_url = dload_url


def publish_story(story):
    
    story.is_published = False 

    file_save_path = story.get_filesave_path()
    
    remove_dir_files(file_save_path, []) 
    
    pmos = PageMediaObject.objects.filter(page__story = story, media_type='image')
    
    for pmo in pmos:
        create_download_media(pmo, story)
        pmo.save()
    
    
    create_story_thumbnail(story, file_save_path)
    # story.save()
    try: 
        story_to_xml(story, file_save_path)
    except IOError:
        msg = 'error creating xml version of story'
        story.is_published = False 
        
    create_story_nomedia_file(file_save_path)
    if not create_story_thumbnail(story, file_save_path):
        msg = 'error creating thumbnail'
        story.is_published = False 
    
    if not create_story_zip(story, file_save_path):
        msg = 'error creating downloadable media'
        story.is_published = False
    else: 
        story.is_published = True
    
    story.save()


def story_to_xml(story, save_path):
    pages = story.page_set.order_by('page_number')
    title = story.title.lower().replace(' ', '')
    title = unidecode(title)
    file_name = save_path + title + '.xml'
    
    stringbuilder = StringIO.StringIO()

    #If file w/ this name already exists, will be overwritten.
    stringbuilder.write('<?xml version="1.0"?> \n')
    stringbuilder.write('<book id="' + str(story.id) + '">' + '\n')
    stringbuilder.write('    <author>' + story.creator_name + '</author> \n')
    stringbuilder.write('    <title>' + story.title.encode('utf8') + '</title> \n')
    stringbuilder.write('    <genre>' + story.genre + '</genre> \n')
    stringbuilder.write('    <pub_date>' + str(story.pub_date.year) + '-' + str(story.pub_date.day)
            + '-' + str(story.pub_date.month) + '</pub_date> \n')
    stringbuilder.write('    <description>' + story.description.encode('utf8') + '</description> \n')
    stringbuilder.write('    <book_pages number_pages="' + str(len(pages)) + '"> \n')

    for p in pages:
        stringbuilder.write('        <page page_number="' + str(p.page_number) + '"> \n')
        pmos = p.pagemediaobject_set.order_by('z_index')
        for pmo in pmos:
            mo_type = pmo.media_type
            xcoor = str(pmo.xcoor)
            ycoor = str(pmo.ycoor)
            width = str(pmo.width) 
            height = str(pmo.height)
            z_index = str(pmo.z_index)
            goto_page = str(pmo.goto_page)
            anime_code = str(pmo.anime_code)
            animate_on = str(pmo.animate_on)
            font_style = pmo.font_style
            font_color = pmo.font_color
            font_size = str(pmo.font_size)
            if mo_type == 'image':
                url = pmo.download_media_url
                start = url.rfind('/') + 1
                url = url[start:]
                output = '<media_object type="' + mo_type \
                        + '" url="' + url + '" xcoor="' + xcoor  \
                        + '" ycoor="' + ycoor + '" z_index="' + z_index  \
                        + '" width="' + width + '" height="' + height  \
                        + '" goto_page="'  + goto_page  \
                        + '" anime_code="' + anime_code  \
                        + '" animate_on="' + animate_on + '"></media_object>' + '\n'
                stringbuilder.write(output.encode('UTF-8'))
                #NOTE: at some point may have associated text with image... 
            elif mo_type == 'text':
                assoc_text = pmo.assoc_text or ''
                assoc_text = assoc_text.replace("\n", "&#10;")
                output = '<media_object type="' + mo_type  \
                        + '" xcoor="' + xcoor + '" ycoor="' + ycoor  \
                        + '" width="' + width + '" height="' + height  \
                        + '" z_index="' + z_index  \
                        + '" font_style="' + font_style  \
                        + '" font_size="' + font_size  \
                        + '" font_color="' + font_color  \
                        + '" goto_page="'  + goto_page  \
                        + '" anime_code="' + anime_code  \
                        + '" animate_on="' + animate_on + '">'  \
                        + assoc_text + '</media_object>' + '\n'
                stringbuilder.write(output.encode('UTF-8'))
            else:
                pass
        stringbuilder.write('        </page> \n')
    stringbuilder.write('    </book_pages> \n')

    stringbuilder.write('</book>')
    
    
    f = open(file_name, 'w')
    f.write(stringbuilder.getvalue())
    f.close()


#TODO probably should have some error checking and ability
# to handel exceptions
def create_story_nomedia_file(save_path):
    ''' .nomedia file used on Android so that media is not
    indexed by os. The .nomedia file is empty and should
    be located in any directory that contains media
    (images, audio, etc.) for the story.
    '''
    file_name = save_path + '.nomedia'
    f = open(file_name, 'w')
    f.write('')
    f.close()

''' create_story_thumbnail
    It is assumed that the story has been created (shared) already
    and therefore it is getting images for composite from the 
    directory with all story media in it. 

    IMPORTANT: no error checking yet, should consider this code fragile 
'''
def create_story_thumbnail(story, save_path):
    ''' Take first page of story and create a composite image of page
        then resize it to our thumbnail size. Recall that the default
        story page is 1280x800
    '''
    
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    page = story.page_set.get(page_number=0)
    pmos = page.pagemediaobject_set.filter(media_type='image').order_by('z_index')
    comp_info = ''
    for pmo in pmos:
        if pmo.download_media_url:
            filename = save_path + os.path.split(pmo.download_media_url)[1] 
            comp_info += filename+' '+ ' -geometry +'+str(pmo.xcoor)+'+'+str(pmo.ycoor)+' -composite '

    cmd1 = 'convert -size 1280x800 xc:white ' + comp_info + save_path + 'thumbnail_icon_large.png'
    commands.getoutput( cmd1 )
    
    # NOTE: this will preserve aspect ratio and result in image 
    # that has an x or y no greater than STORY_THUMBNAIL_SIZE
    cmd2 = 'convert -resize {0}x{0} {1}thumbnail_icon_large.png {1}thumbnail_icon.png'.format(STORY_THUMBNAIL_SIZE, save_path)
    result = commands.getoutput( cmd2 )
    
    # if result not '' then some type of error 
    return True if result == '' else False 


def create_story_zip(story, save_path):
    # replace spaces with underscores 
    title = story.title.replace(" ", "_") 
    title = unidecode(title)
    cmd = 'zip -rj ' + save_path + title + '.zip' + ' ' + save_path
    result = commands.getoutput( cmd ) 
    return False if (result.find('warning') >= 0 or result.find('error') >= 0) else True
    

def remove_dir_files(dir_path, exempt=[]): 
# dir_path should have ending '/'
# exempt is a list of files that should not be removed 
    if not os.path.exists(dir_path): 
        return
    dl = os.listdir(dir_path)
    for f in dl:
        if not f in exempt:
        # remove file, error if dir 
            os.remove(dir_path+f)

