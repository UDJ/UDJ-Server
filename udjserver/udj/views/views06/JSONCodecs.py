import json
from udj.models import SongSet
from udj.models import SongSetEntry
from udj.models import Player
from udj.models import PlayerAdmin
from udj.models import PlayerLocation
from udj.models import PlayerPassword
from udj.models import PlaylistEntryTimePlayed
from udj.models import Participant
from udj.models import LibraryEntry
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed
from udj.models import SortingAlgorithm
from udj.models import ExternalLibrary
from udj.models import Favorite

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.contrib.auth.models import User


class UDJEncoder(json.JSONEncoder):

  def default(self, obj):
    if isinstance(obj, QuerySet):
      return [x for x in obj]
    elif isinstance(obj, Favorite):
      return obj.favorite_song
    elif isinstance(obj, ExternalLibrary):
      return {
        'id' : str(obj.id),
        'name' : obj.name,
        'description' : obj.description
      }
    elif isinstance(obj, SortingAlgorithm):
      return {
        'id' : str(obj.id),
        'name' : obj.name,
        'description' : obj.description
      }
    elif isinstance(obj, User):
      return {
        'id' : str(obj.id),
        'username' : obj.username,
        'first_name' : obj.first_name,
        'last_name' : obj.last_name
      }
    elif isinstance(obj, ActivePlaylistEntry):
      toReturn =  {
        'song' : obj.song,
        'upvoters' : obj.upvoters(),
        'downvoters' : obj.downvoters(),
        'time_added' : obj.time_added.replace(microsecond=0).isoformat(),
        'adder' : obj.adder
      }

      if obj.state == 'PL' or obj.state == 'FN':
        toReturn['time_played'] = PlaylistEntryTimePlayed.objects.get(playlist_entry=obj).time_played.replace(microsecond=0).isoformat()
      return toReturn

    elif isinstance(obj, LibraryEntry):
      return {
          'id' : obj.lib_id,
          'title' : obj.title,
          'artist' : obj.artist,
          'album' : obj.album,
          'track' : obj.track,
          'genre' : obj.genre,
          'duration' : obj.duration
      }

    elif isinstance(obj, Participant):
      return obj.user
    elif isinstance(obj, PlayerAdmin):
      return obj.admin_user
    elif isinstance(obj, Player):
      toReturn = {
        "id" : str(obj.id),
        "name" : obj.name,
        "owner" : obj.owning_user,
        "has_password" : True if PlayerPassword.objects.filter(player=obj).exists() else False,
        "admins" : obj.Admins(),
        "sorting_algo": obj.sorting_algo,
        "songset_user_permission" : obj.allow_user_songset,
        "num_active_users" : len(obj.ActiveParticipants()),
        "external_libraries": obj.ExternalLibraries(),
        "size_limit" : obj.size_limit if obj.size_limit != None else 0
      }

      try:
        toReturn['location'] = PlayerLocation.objects.get(player=obj)
      except ObjectDoesNotExist:
        pass
      
      if obj.size_limit != None:
        toReturn['size_limit'] = obj.size_limit

      return toReturn
    elif isinstance(obj, PlayerLocation):
      return {
          "address" : obj.address if obj.address != None else "",
          "locality" : obj.locality if obj.locality != None else "",
          "region" : obj.region if obj.region != None else "",
          "country" : obj.country,
          "postal_code" : obj.postal_code,
          "latitude" : obj.point.y,
          "longitude" : obj.point.x
      }
    elif isinstance(obj, SongSet):
      return {
          "name" : obj.name,
          "description" : obj.description,
          "songs" : obj.Songs(),
          "owner" : obj.owner,
          "date_created" : obj.date_created.replace(microsecond=0).isoformat()
      }


    elif isinstance(obj, SongSetEntry):
      return obj.song

    elif isinstance(obj, PlaylistEntryTimePlayed):
      return obj.playlist_entry

    return json.JSONEncoder.default(self, obj)


