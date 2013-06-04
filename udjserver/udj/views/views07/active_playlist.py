import json

from udj.views.views07.JSONCodecs import UDJEncoder
from udj.headers import MISSING_RESOURCE_HEADER
from udj.views.views07.responses import HttpJSONResponse, HttpResponseMissingResource
from udj.models import Participant, Player, ActivePlaylistEntry, LibraryEntry, Vote
from udj.views.views07.decorators import (PlayerExists,
                                          PlayerIsActive,
                                          AcceptsMethods,
                                          UpdatePlayerActivity,
                                          HasNZJSONParams)
from udj.views.views07.authdecorators import (NeedsAuth,
                                              HasPlayerPermissions,
                                              IsOwnerOrParticipates)

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

def getAlreadyOnPlaylist(songs, player):
  return filter(lambda x: ActivePlaylistEntry.isQueuedOrPlaying(x['id'], x['library_id'], player),
                songs)

def getNotOnPlaylist(songs, player):
  return filter(lambda x: not ActivePlaylistEntry.isQueued(x['id'], x['library_id'], player), songs)

def addSongsToPlaylist(songs, activePlayer, user):
  for song in songs:
    libEntry = LibraryEntry.objects.get(library__id=int(song['library_id']), lib_id=song['id'])

    addedEntry = ActivePlaylistEntry(song=libEntry, adder=user, player=activePlayer)
    addedEntry.save()

    Vote(playlist_entry=addedEntry, user=user, weight=1).save()

def removeSongsFromPlaylist(songs, activePlayer, user):
  for song in songs:
    playlistEntry = ActivePlaylistEntry.objects.get(
      song__library__id=int(song['library_id']),
      song__lib_id=song['id'],
      state='QE')
    playlistEntry.state='RM'
    playlistEntry.save()



@csrf_exempt
@AcceptsMethods(['GET', 'POST'])
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@transaction.commit_on_success
def activePlaylist(request, player_id, player):
  if request.method == 'GET':
    return getActivePlaylist(player)
  else:
    return multiModActivePlaylist(request, player)

def getActivePlaylist(player):
  return HttpJSONResponse(json.dumps(player.ActivePlaylist, cls=UDJEncoder))

@HasPlayerPermissions(['APR', 'APA'])
@HasNZJSONParams(['to_add','to_remove'])
def multiModActivePlaylist(request, player, json_params):


  """
  Code so ugly.....
  """

  player.lockActivePlaylist()
  toAdd = json_params['to_add']
  toRemove = json_params['to_remove']


  try:
    #first, validate/process all our inputs
    # 1. Ensure none of the songs to be deleted aren't on the playlist
    notOnPlaylist = getNotOnPlaylist(toRemove, player)
    if len(notOnPlaylist) > 0:
      toReturn = HttpJSONResponse(json.dumps(notOnPlaylist), status=404)
      toReturn[MISSING_RESOURCE_HEADER] = 'song'
      return toReturn

    # 2. Ensure all of the songs to be added actually exists in the library
    notInLibrary = filter(lambda x: not LibraryEntry.songExsitsAndNotBanned(x['id'],
                                                                            int(x['library_id']),
                                                                            player),
                          toAdd)
    if len(notInLibrary) > 0:
      print "About to print not in library"
      toReturn = HttpJSONResponse(json.dumps(notInLibrary), content_type="text/json", status=404)
      toReturn[MISSING_RESOURCE_HEADER] = 'song'
      return toReturn

    # 3. See if there are any songs that we're trying to add that are already on the playlist
    # and vote them up instead.
    alreadyOnPlaylist = getAlreadyOnPlaylist(toAdd, player)
    toAdd = filter(lambda x: x not in alreadyOnPlaylist, toAdd)
    try:
      currentSong = ActivePlaylistEntry.objects.get(player=player, state='PL')
    except ObjectDoesNotExist:
      currentSong = None
    for song in alreadyOnPlaylist:
      #make sure we don't vote on the currently playing song
      if (currentSong != None and not 
           (currentSong.song.lib_id == song['id'] 
            and currentSong.song.library.id == int(song['library_id']))):
        voteSong(player, request.udjuser, song['id'], int(song['library_id']), 1)

    #alright, we should be good to go. Let's actually add/remove songs
    #Note that we didn't make any actual changes to the DB until we were sure all of our inputs
    #were good and we weren't going to return an error HttpResponse. This is what allows us to use
    #the commit on success
    addSongsToPlaylist(toAdd, player, request.udjuser)
    removeSongsFromPlaylist(toRemove, player, request.udjuser)
  except ValueError:
    return HttpResponseBadRequest('Value Error. Bad JSON\n' + 'toAdd: ' + str(toAdd) + '\ntoRemove: ' + str(toRemove))
  except TypeError as te:
    return HttpResponseBadRequest('Bad JSON\n' + 'toAdd: ' + str(toAdd) + '\ntoRemove: ' + str(toRemove) + str(te))
  except KeyError:
    return HttpResponseBadRequest('KeyError Bad JSON\n' + 'toAdd: ' + str(toAdd) + '\ntoRemove: ' + str(toRemove))


  return HttpResponse()


@csrf_exempt
@NeedsAuth
@AcceptsMethods(['PUT', 'DELETE'])
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@transaction.commit_on_success
def modActivePlaylist(request, player_id, player, library_id, song_id):
  if request.method == 'PUT':
    return add2ActivePlaylist(request, song_id, library_id, player)
  elif request.method == 'DELETE':
    return removeFromActivePlaylist(request, request.udjuser, song_id, library_id, player)


@HasPlayerPermissions(['APA'], player_arg_position=3)
def add2ActivePlaylist(request, song_id, library_id, player):
  player.lockActivePlaylist()
  if ActivePlaylistEntry.isQueued(song_id, library_id, player):
    voteSong(player, request.udjuser, song_id, library_id, 1)
    return HttpResponse()
  elif ActivePlaylistEntry.isPlaying(song_id, library_id, player):
    return HttpResponse()

  if LibraryEntry.songExsitsAndNotBanned(song_id, library_id, player):
    addSongsToPlaylist([{'id' : song_id , 'library_id' : library_id}], player, request.udjuser)
  else:
    return HttpResponseMissingResource('song')

  return HttpResponse(status=201)

@HasPlayerPermissions(['APR'], player_arg_position=4)
def removeFromActivePlaylist(request, user, song_id, library_id, player):
  player.lockActivePlaylist()
  try:
    removeSongsFromPlaylist([{'id' : song_id, 'library_id' : library_id}], player, user)
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('song')

  return HttpResponse()



@csrf_exempt
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@AcceptsMethods(['POST', 'PUT'])
def voteSongDown(request, player_id, lib_id, player):
  return voteSong(player, request.udjuser, lib_id, -1)

@csrf_exempt
@NeedsAuth
@PlayerExists
@PlayerIsActive
@IsOwnerOrParticipates
@UpdatePlayerActivity
@AcceptsMethods(['POST', 'PUT'])
def voteSongUp(request, player_id, lib_id, player):
  return voteSong(player, getUserForTicket(request), lib_id, 1)

def voteSong(player, user, song_id, library_id, weight):

  try:
    playlistEntry = ActivePlaylistEntry.objects.get(
        player=player,
        song__lib_id=song_id,
        song__library__id=library_id,
        state='QE')
  except ObjectDoesNotExist:
    toReturn = HttpResponseNotFound()
    toReturn[MISSING_RESOURCE_HEADER] = 'song'
    return toReturn

  vote, created = Vote.objects.get_or_create(playlist_entry=playlistEntry, user=user,
      defaults={'weight': weight})

  if not created:
    vote.weight = weight
    vote.save()

  return HttpResponse()
