"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

#from django.test import TestCase

from storyscape.models import Story, Page, PageMediaObject

"""
class SimpleTest(TestCase):
    def test_basic_addition(self):
        
        #Tests that 1 + 1 always equals 2.
        
        self.assertEqual(1 + 1, 2)
"""

def get_xml_info():
    s = Story.objects.get(is_published=True)
    for p in Page.objects.filter(story=s):
        print 'On page ' + str(p.page_number) + '\n'
        for pmo in PageMediaObject.objects.filter(page=p):
            print 'page media object info:' + '\n'
            print 'type ' + pmo.media_type + '\n'
            print 'xcoor ' + str(pmo.xcoor) + ', ycoor ' + str(pmo.ycoor) + '\n'
            print 'anime_code ' + str(pmo.anime_code) + '\n'
            if pmo.media_type == 'image':
                m = pmo.media_object
                print 'http_src ' + m.url + '\n'
                print 'name ' + m.name + m.format.label + '\n'
            elif pmo.media_type == 'text':
                print 'asso. text: ' + pmo.assoc_text + '\n'
            else:
                pass
            

def print_xml3(s):   #s is a Story object for which is_published=True
    pages = s.page_set.order_by('page_number')
    file_name = s.title + '-XML.xml'
    f = open(file_name, 'w')   
    #Creates a new file if none of this name exists.  
    #If file w/ this name already exists, will be overwritten.
    f.write('<?xml version="1.0"?> \n')
    f.write('<story id="' + str(s.id) + '">' + '\n')
    f.write('    <author>' + s.creator_name + '</author> \n')
    f.write('    <title>' + s.title + '</title> \n')
    f.write('    <genre>' + s.genre + '</genre> \n')
    f.write('    <pub_date>' + str(s.pub_date.year) + '-' + str(s.pub_date.day) 
            + '-' + str(s.pub_date.month) + '</pub_date> \n')
    f.write('    <description>' + s.description + '</description> \n')
    f.write('    <story_pages number_pages="' + str(len(pages)) + '"> \n')
    
    for p in pages:
        f.write('        <page page_number="' + str(p.page_number) + '"> \n')
        pmos = p.pagemediaobject_set.all() 
        for pmo in pmos:
            xcoor = str(pmo.xcoor)
            ycoor = str(pmo.ycoor)
            anime_code = str(pmo.anime_code)
            animate_on = str(pmo.animate_on)
            if type == 'image':
                m = pmo.media_object
                name = m.name + '.' + m.format.label
                root_src = 'http://sodiioo.media.mit.edu/media/storyscape_media/stories/'
                http_src = root_src + pmo.download_media_url
                f.write('            <media_object type="' + type + '" http_src="' + http_src
                        + '" name="' + name + '" xcoor="' + xcoor + '" ycoor="' + ycoor
                        + '" anime_code="' + anime_code 
                        + '" animate_on="' + animate_on + '"></media_object>' + '\n')
            elif type == 'text':
                assoc_text = pmo.assoc_text
                f.write('            <media_object type="' + type + '" xcoor="' + xcoor 
                        + '" ycoor="' + ycoor + '" anime_code="' + anime_code + '"> '
                        + assoc_text + '</media_object>' + '\n')
            else:
                pass
        f.write('        </page> \n')       
    f.write('    </story_pages> \n')
    
    f.write('</story>')
    f.close()
    print 'Done'
    return 0

s1 = Story.objects.get(id=17)
print 'Done'
