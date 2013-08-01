import commands
import os

''' Utility methods used by storyscape. 
    Developer: Micah Eckhardt
    Creation date: 08-21-12
'''

def story_to_xml(story, save_path):
    pages = story.page_set.order_by('page_number')
    title = story.title.lower().replace(' ', '')
    file_name = save_path + title + '.xml'
    try:
        f = open(file_name, 'w')
    except IOError as e: raise

    #If file w/ this name already exists, will be overwritten.
    f.write('<?xml version="1.0"?> \n')
    f.write('<book id="' + str(story.id) + '">' + '\n')
    f.write('    <author>' + story.creator_name + '</author> \n')
    f.write('    <title>' + story.title + '</title> \n')
    f.write('    <genre>' + story.genre + '</genre> \n')
    f.write('    <pub_date>' + str(story.pub_date.year) + '-' + str(story.pub_date.day)
            + '-' + str(story.pub_date.month) + '</pub_date> \n')
    f.write('    <description>' + story.description + '</description> \n')
    f.write('    <book_pages number_pages="' + str(len(pages)) + '"> \n')

    for p in pages:
        f.write('        <page page_number="' + str(p.page_number) + '"> \n')
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
                m = pmo.media_object
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
                f.write(output.encode('UTF-8'))
                #NOTE: at some point may have associated text with image... 
            elif mo_type == 'text':
                assoc_text = pmo.assoc_text
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
                f.write(output.encode('UTF-8'))
            else:
                pass
        f.write('        </page> \n')
    f.write('    </book_pages> \n')

    f.write('</book>')
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
    page = story.page_set.get(page_number=0)
    pmos = page.pagemediaobject_set.filter(media_type='image').order_by('z_index')
    comp_info = ''
    for pmo in pmos:
        #NOTE: can have attribute error if no download_media_url defined. 
        file = save_path + os.path.split(pmo.download_media_url)[1] 
        comp_info += file+' '+ ' -geometry +'+str(pmo.xcoor)+'+'+str(pmo.ycoor)+' -composite '
        # should include some error checking someday 

    cmd1 = 'convert -size 1280x800 xc:white ' + comp_info + save_path + 'thumbnail_icon.png'
    result = commands.getoutput( cmd1 )
    
    # if all good need to resize this

    # NOTE: this will preserve aspetc ratio and result in image 
    # that has an x or y no grater than 120px
    cmd2 = 'convert -resize 120x120 ' + save_path + 'thumbnail_icon.png ' + save_path + 'thumbnail_icon.png'
    result = commands.getoutput( cmd2 )
    
    # if result not '' then some type of error 
    return True if result == '' else False 


def create_story_zip(story, save_path):
    # replace spaces with underscores 
    title = story.title.replace(" ", "_") 
    cmd = 'zip -rj ' + save_path + title + '.zip' + ' ' + save_path
    result = commands.getoutput( cmd ) 
    return False if (result.find('warning') >= 0 or result.find('error') >= 0) else True
    

def remove_dir_files(dir_path, exempt=[]): 
# dir_path should have ending '/'
# exempt is a list of files that should not be removed 
    dl = os.listdir(dir_path)
    for f in dl:
        if not f in exempt:
        # remove file, error if dir 
            os.remove(dir_path+f)

