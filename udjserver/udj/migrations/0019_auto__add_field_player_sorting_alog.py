# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from udj.trans_migration_constants import ADDED_DEFAULT_ALGO_NAME



class Migration(SchemaMigration):
    no_dry_run = True

    def forwards(self, orm):
        # Adding field 'Player.sorting_algo'
        defaultAlgo = orm.SortingAlgorithm.objects.get(name=ADDED_DEFAULT_ALGO_NAME)
        db.add_column('udj_player', 'sorting_algo',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=defaultAlgo.id, to=orm['udj.SortingAlgorithm']),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Player.sorting_algo'
        db.delete_column('udj_player', 'sorting_algo_id')

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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'udj.activeplaylistentry': {
            'Meta': {'object_name': 'ActivePlaylistEntry'},
            'adder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.LibraryEntry']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "u'QE'", 'max_length': '2'}),
            'time_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.libraryentry': {
            'Meta': {'object_name': 'LibraryEntry'},
            'album': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'artist': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_banned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"}),
            'player_lib_song_id': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'track': ('django.db.models.fields.IntegerField', [], {})
        },
        'udj.participant': {
            'Meta': {'unique_together': "(('user', 'player'),)", 'object_name': 'Participant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']"}),
            'time_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_last_interaction': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.player': {
            'Meta': {'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owning_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'sorting_algo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.SortingAlgorithm']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'IN'", 'max_length': '2'}),
            'volume': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'udj.playerlocation': {
            'Meta': {'object_name': 'PlayerLocation'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']", 'unique': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'default': "'POINT(0.0 0.0)'"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.State']"}),
            'zipcode': ('django.db.models.fields.IntegerField', [], {})
        },
        'udj.playerpassword': {
            'Meta': {'object_name': 'PlayerPassword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password_hash': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.Player']", 'unique': 'True'}),
            'time_set': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.playlistentrytimeplayed': {
            'Meta': {'object_name': 'PlaylistEntryTimePlayed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist_entry': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['udj.ActivePlaylistEntry']", 'unique': 'True'}),
            'time_played': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'udj.sortingalgorithm': {
            'Meta': {'object_name': 'SortingAlgorithm'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'function_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'udj.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'udj.ticket': {
            'Meta': {'unique_together': "(('user', 'ticket_hash'),)", 'object_name': 'Ticket'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket_hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'time_issued': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'udj.vote': {
            'Meta': {'unique_together': "(('user', 'playlist_entry'),)", 'object_name': 'Vote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playlist_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['udj.ActivePlaylistEntry']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['udj']