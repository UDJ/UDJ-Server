import json

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

from settings import RESTRICTED_LIBRARY_NAMES


from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

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
    to_return = to_return.filter(library__owned_library__owner__id=(int(request.GET['owner'])))

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

@HasLibrary
@HasLibraryWritePermission
def delete_library(request, library_id, library):
  library.is_deleted = True
  library.save()
  LibraryEntry.objects.filter(library=library).update(is_deleted=True)
  AssociatedLibrary.objects.filter(library=library).update(enabled=False)
  return HttpResponse()

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
