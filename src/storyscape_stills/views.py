
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.db.models.query import QuerySet
from django.utils.html import strip_tags

from django.contrib.auth.models import User
from django.core import serializers
import settings
import simplejson


def storyscape_stills(request, story_id):    
    return render( request, 'storyscape_stills.html', {} )



