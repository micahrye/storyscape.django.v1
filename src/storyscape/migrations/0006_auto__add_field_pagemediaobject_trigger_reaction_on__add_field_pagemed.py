# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PageMediaObject.trigger_reaction_on'
        db.add_column('storyscape_pagemediaobject', 'trigger_reaction_on',
                      self.gf('django.db.models.fields.IntegerField')(default=0, blank=True),
                      keep_default=False)

        # Adding field 'PageMediaObject.reaction_object'
        db.add_column('storyscape_pagemediaobject', 'reaction_object',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'PageMediaObject.trigger_reaction_on'
        db.delete_column('storyscape_pagemediaobject', 'trigger_reaction_on')

        # Deleting field 'PageMediaObject.reaction_object'
        db.delete_column('storyscape_pagemediaobject', 'reaction_object')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'avatar_type': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'bronze': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'consecutive_days_visit_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'display_tag_filter_strategy': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_isvalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_key': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'email_signature': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_tag_filter_strategy': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gold': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'gravatar': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignored_tags': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'interesting_tags': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_fake': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'new_response_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'questions_per_page': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'reputation': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'seen_response_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_country': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_marked_tags': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'silver': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'w'", 'max_length': '2'}),
            'subscribed_tags': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'medialibrary.mediaformat': {
            'Meta': {'object_name': 'MediaFormat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '10'})
        },
        'medialibrary.mediaobject': {
            'Meta': {'object_name': 'MediaObject'},
            'creation_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'format': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['medialibrary.MediaFormat']", 'blank': 'True'}),
            'has_tag': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'default': "'http://web.resource.org/cc/PublicDomain'", 'max_length': '60', 'blank': 'True'}),
            'mo_tags': ('tagging.fields.TagField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'imagefile'", 'max_length': '60', 'blank': 'True'}),
            'original': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publisher': ('django.db.models.fields.CharField', [], {'default': "'Sodiioo'", 'max_length': '60', 'blank': 'True'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_rel_+'", 'blank': 'True', 'to': "orm['medialibrary.MediaObject']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['medialibrary.MediaType']", 'blank': 'True'}),
            'upload_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '60', 'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'blank': 'True'})
        },
        'medialibrary.mediatype': {
            'Meta': {'object_name': 'MediaType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'})
        },
        'storyscape.page': {
            'Meta': {'object_name': 'Page'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page_number': ('django.db.models.fields.IntegerField', [], {}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['storyscape.Story']"})
        },
        'storyscape.pagemediaobject': {
            'Meta': {'object_name': 'PageMediaObject'},
            'animate_on': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'anime_code': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'assoc_text': ('django.db.models.fields.CharField', [], {'max_length': '16384', 'null': 'True', 'blank': 'True'}),
            'download_media_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'font_color': ('django.db.models.fields.CharField', [], {'default': "'#000000'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'font_size': ('django.db.models.fields.IntegerField', [], {'default': '48', 'null': 'True', 'blank': 'True'}),
            'font_style': ('django.db.models.fields.CharField', [], {'default': "'sans_serif'", 'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'goto_page': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['medialibrary.MediaObject']", 'null': 'True'}),
            'media_type': ('django.db.models.fields.CharField', [], {'default': "'image'", 'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['storyscape.Page']"}),
            'reaction_object': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'trigger_reaction_on': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'xcoor': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ycoor': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'z_index': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'storyscape.story': {
            'Meta': {'object_name': 'Story'},
            'creation_datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'creator_uid': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '16384'}),
            'download_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'thumb_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'storyscape.storylibrary': {
            'Meta': {'object_name': 'StoryLibrary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['storyscape.Story']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['storyscape']