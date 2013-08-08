# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MediaType'
        db.create_table('medialibrary_mediatype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(default='unknown', max_length=20)),
        ))
        db.send_create_signal('medialibrary', ['MediaType'])

        # Adding model 'MediaFormat'
        db.create_table('medialibrary_mediaformat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(default='unknown', max_length=10)),
        ))
        db.send_create_signal('medialibrary', ['MediaFormat'])

        # Adding model 'MediaObject'
        db.create_table('medialibrary_mediaobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='imagefile', max_length=60, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['medialibrary.MediaType'], blank=True)),
            ('format', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['medialibrary.MediaFormat'], blank=True)),
            ('publisher', self.gf('django.db.models.fields.CharField')(default='Sodiioo', max_length=60, blank=True)),
            ('license', self.gf('django.db.models.fields.CharField')(default='http://web.resource.org/cc/PublicDomain', max_length=60, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('upload_image', self.gf('django.db.models.fields.files.ImageField')(max_length=60, null=True)),
            ('has_tag', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('medialibrary', ['MediaObject'])

        # Adding M2M table for field related on 'MediaObject'
        db.create_table('medialibrary_mediaobject_related', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_mediaobject', models.ForeignKey(orm['medialibrary.mediaobject'], null=False)),
            ('to_mediaobject', models.ForeignKey(orm['medialibrary.mediaobject'], null=False))
        ))
        db.create_unique('medialibrary_mediaobject_related', ['from_mediaobject_id', 'to_mediaobject_id'])

        # Adding model 'MediaLibrary'
        db.create_table('medialibrary_medialibrary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('medialibrary', ['MediaLibrary'])

        # Adding M2M table for field media_object on 'MediaLibrary'
        db.create_table('medialibrary_medialibrary_media_object', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('medialibrary', models.ForeignKey(orm['medialibrary.medialibrary'], null=False)),
            ('mediaobject', models.ForeignKey(orm['medialibrary.mediaobject'], null=False))
        ))
        db.create_unique('medialibrary_medialibrary_media_object', ['medialibrary_id', 'mediaobject_id'])

        # Adding model 'ImageObject'
        db.create_table('medialibrary_imageobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=60, null=True)),
        ))
        db.send_create_signal('medialibrary', ['ImageObject'])

        # Adding model 'ImageObject2'
        db.create_table('medialibrary_imageobject2', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=60, null=True)),
        ))
        db.send_create_signal('medialibrary', ['ImageObject2'])


    def backwards(self, orm):
        # Deleting model 'MediaType'
        db.delete_table('medialibrary_mediatype')

        # Deleting model 'MediaFormat'
        db.delete_table('medialibrary_mediaformat')

        # Deleting model 'MediaObject'
        db.delete_table('medialibrary_mediaobject')

        # Removing M2M table for field related on 'MediaObject'
        db.delete_table('medialibrary_mediaobject_related')

        # Deleting model 'MediaLibrary'
        db.delete_table('medialibrary_medialibrary')

        # Removing M2M table for field media_object on 'MediaLibrary'
        db.delete_table('medialibrary_medialibrary_media_object')

        # Deleting model 'ImageObject'
        db.delete_table('medialibrary_imageobject')

        # Deleting model 'ImageObject2'
        db.delete_table('medialibrary_imageobject2')


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
        'medialibrary.imageobject': {
            'Meta': {'object_name': 'ImageObject'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '60', 'null': 'True'})
        },
        'medialibrary.imageobject2': {
            'Meta': {'object_name': 'ImageObject2'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '60', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'medialibrary.mediaformat': {
            'Meta': {'object_name': 'MediaFormat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '10'})
        },
        'medialibrary.medialibrary': {
            'Meta': {'object_name': 'MediaLibrary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_object': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['medialibrary.MediaObject']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'medialibrary.mediaobject': {
            'Meta': {'object_name': 'MediaObject'},
            'creation_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'format': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['medialibrary.MediaFormat']", 'blank': 'True'}),
            'has_tag': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'default': "'http://web.resource.org/cc/PublicDomain'", 'max_length': '60', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'imagefile'", 'max_length': '60', 'blank': 'True'}),
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
        }
    }

    complete_apps = ['medialibrary']