import json

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from udj.views.views07.JSONCodecs import UDJEncoder
from udj.models import Library
from udj.views.views07.decorators import (HasPagingSemantics,
                                          AcceptsMethods,
                                          HasNZJSONParams,
                                          NeedsJSON)
from udj.views.views07.responses import (HttpJSONResponse,
                                         HttpResponseForbiddenWithReason,
                                         HttpResponseMissingResource)
from udj.views.views07.authdecorators import (NeedsAuth,
                                              HasLibraryReadPermission,
                                              HasLibraryWritePermission)
def addSongs(toAdd, library):
  for song in toAdd:
    newSong = LibraryEntry(library=library,
                           lib_id=song['id'],
                           title=song['title'],
                           artist=song['artist'],
                           album=song['album'],
                           track=song['track'],
                           genre=song['genre'],
                           duration=song['duration']
                          )
    newSong.save()

def deleteSongs(toDelete, library):
  for song_id in toDelete:
    LibraryEntry.objects.get(library=library, lib_id=song_id).deleteSong()

def getNonExistantLibIds(songIds, library):
  return filter(lambda x: not LibraryEntry.songExists(x, library.id, player), songIds)

def getDuplicateAndConflictingIds(songs, library):
  #This funciton seems like a potential performance bottleneck
  conflictingIds = []
  duplicateIds = []
  for song in songs:
    potentialDuplicate = LibraryEntry.objects.filter(library=library,
                                                     lib_id=song['id'],
                                                     is_deleted=False)
    if potentialDuplicate.exists():
      duplicateIds.append(song['id']) 
      if (potentialDuplicate[0].title != song['title'] or
          potentialDuplicate[0].artist != song['artist'] or
          potentialDuplicate[0].album != song['album'] or
          potentialDuplicate[0].track != song['track'] or
          potentialDuplicate[0].genre != song['genre'] or
          potentialDuplicate[0].duration != song['duration']):
        conflictingIds.append(song['id'])
  return (duplicateIds, conflictingIds)

def HasLibrary(library_id_arg_pos=1):
  def decorator(target)
    def wrapper(*args, **kwargs)
      try:
        kwargs['library'] = Library.objects.get(pk=int(library_id))
        return target(*args, **kwargs)
      except ObjectDoesNotExist:
        return HttpResponseMissingResource('library')
    return wrapper
  return decorator

def HasLibraryWritePermission(funciton):
  def wrapper(*args, **kwargs)
    user = args[0].udjuser
    library = kwargs['library']
    if library.user_has_write_perm(user):
      return function(*args, **kwargs)
    else
      return HttpResponseForbiddenWithReason('write-permission')
  return wrapper

@NeedsAuth
@AcceptsMethods(['GET', 'PUT'])
@transaction.commit_on_success
def libraries(request):
  if request.method == 'GET':
    return get_libraries(request)
  else:
    return create_library(request)


@HasPagingSemantics
def get_libraries(request, max_results, offset)
  max_results = min(max_results, 200)
  to_return = Library.objects.all()

  if 'name' in request.GET:
    to_return = to_return.filter(name__icontains=request.GET['name'])

  if 'owner' in request.GET:
    #Ok, this next line may not be quite right, I forgot how to do many to many relationships
    to_return = to_return.filter(owner__id=(int(request.GET['owner'])))

  if 'is_readable' in request.GET:
    to_return = filter(lambda x: x.user_has_read_perm(request.udjuser))

  to_return = to_return[offset:offset+max_results]

  return HttpJSONResponse(json.dumps(to_return, cls=UDJEncoder))

@csrf_exempt
@HasNZJSONParams(['name', 'description', 'public_key'])
def create_library(request, json_params):
  new_library = Library(name=json_params['name'],
                        description=json_params['description'],
                        public_key=json_params['public_key']
                       )
  new_library.save()
  new_owned_library = OwnedLibrary(library=new_library, owner=request.udjuser)
  new_owned_library.save()
  return HttpJSONResponse(json.dumps(new_library, cls=UDJEncoder))

@NeedsAuth
@AcceptsMethods(['GET', 'DELETE', 'POST'])
@transaction.commit_on_success
def library(request, library_id):
  if request.method == 'GET':
    return get_library_info(library_id)
  elif request.method == 'DELETE':
    return delete_library(request, library_id)
  else:
    return mod_library(library_id)

@HasLibrary(library_id_arg_pos=0)
def get_library_info(library_id, library):
  return HttpJSONResponse(json.dumps(library, cls=UDJEncoder))

@csrf_exempt
@HasLibrary
@HasLibraryWritePermission
def delete_library(request, library_id, library):
  library.is_deleted = True
  library.save()
  LibraryEntry.objects.filter(library=library).update(is_deleted=True)
  AssociatedLibrary.objects.filter(library=library).update(enabled=False)
  return HttpResponse()

@csrf_exempt
@HasLibrary
@HasLibraryWritePermission
def mod_library(request, library_id, library):
  json = ""
  try:
    json = json.loads(request.raw_post_data)
  except ValueError:
    return HttpResponseBadRequest('Bad JSON')

  if 'name' in json:
    library.name = json['name']
  if 'description' in json:
    library.description = json['description']
  if 'public_key' in json:
    library.public_key = json['public_key']

  library.save()
  return HttpResponse()


@csrf_exempt
@HasLibrary
@HasLibraryWritePermission
@AcceptsMethods(['PUT', 'POST'])
@csrf_exempt
@transaction.commit_on_success
def songs(request, library_id, library):
  if request.method == 'PUT':
    return addSingleSong(request, library)
  elif request.method == 'POST':
    return libraryMultiMod(request, library)

@HasNZJSONParams(['id', 'title', 'artist', 'album', 'genre', 'track', 'duration'])
def addSingleSong(request, library, json_params):
  duplicateIds, conflictingIds = getDuplicateAndConflictingIds(json_params)
  if len(duplicateIds) > 0:
    return HttpResponse()
  if len(conflictingIds) > 0:
    return HttpResponse(status=409)

  addSongs([json_params], library)
  return HttpResponse()

@HasNZJSONParams(['to_add', 'to_delete'])
def libraryMultiMod(request, library, json_params):

  try:
    duplicateIds, conflictingIds = getDuplicateAndConflictingIds(json_params['to_add'])
    if len(conflictingIds) > 0:
      return HttpResponse(json.dumps(conflictingIds), status=409)

    nonExistentIds = getNonExistantLibIds(json_params['to_delete'], library)
    if len(nonExistentIds) > 0:
      return HttpJSONResponse(json.dumps(nonExistentIds), status=404)

    addSongs(filter(lambda song: song['id'] not in duplicateIds, json_params['to_add'], library))
    deleteSongs(json_params['to_delete'], library)
  except KeyError as e:
    return HttpResponseBadRequest('Bad JSON.\n Bad key: ' + str(e) )
  except ValueError as f:
    return HttpResponseBadRequest('Bad JSON.\n Bad value: ' + str(f) )

  return HttpResponse()



@csrf_exempt
@HasLibrary
@HasLibraryWritePermission
@AcceptsMethods(['DELETE'])
@csrf_exempt
def deleteSong(request, library_id, song_id, library):
  try:
    LibraryEntry.objects.get(library=library, lib_id=song_id).delete()
    return HttpResponse()
  except ObjectDoesNotExist:
    return HttpResponseMissingResource('song')
