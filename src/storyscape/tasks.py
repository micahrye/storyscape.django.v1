from celery import task
from storyscape import utilities
from storyscape.models import Story

@task
def publish_story(story_id):
    story = Story.objects.get(id = story_id)
    utilities.publish_story(story)
    return "Successfully finished publishing your story, {0}!".format(story.title)