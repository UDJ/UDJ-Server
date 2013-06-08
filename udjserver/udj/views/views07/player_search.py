import json

from udj.models import PlayerLocation
from udj.models import Player
from udj.views.views07.authdecorators import NeedsAuth
from udj.views.views07.decorators import AcceptsMethods, HasNZParams, HasPagingSemantics
from udj.views.views07.JSONCodecs import UDJEncoder
from udj.views.views07.responses import HttpJSONResponse, HttpResponseNotAcceptable

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.http import HttpRequest
from django.http import HttpResponse

from settings import DEFAULT_SEARCH_RADIUS, MAX_SEARCH_RADIUS, MIN_SEARCH_RADIUS, DEFAULT_MAX_PLAYER_SEARCH_RESULTS

def hasBadLatLonParams(request):
  if 'latitude' in request.GET and 'longitude' not in request.GET:
    return True
  elif 'longitude' in request.GET and 'latitude' not in request.GET:
    return True
  elif ('latitude' in request.GET and 'longitude' in request.GET and
         (request.GET['latitude'] == "" or request.GET['longitude'] =="")):
    return True
  else:
    return False

@NeedsAuth
@AcceptsMethods(['GET'])
@HasPagingSemantics(DEFAULT_MAX_PLAYER_SEARCH_RESULTS)
def playerSearch(request, max_results, offset):
  if hasBadLatLonParams(request):
    return HttpResponseNotAcceptable('latitude-longitude')

  toReturn = Player.objects.all()

  """
  Note we need this particular if-else chain in order to return
  players ordered by distance if a location is provided
  """
  if 'latitude' in request.GET:
    search_radius = int(request.GET.get('radius', DEFAULT_SEARCH_RADIUS))
    if search_radius >= MAX_SEARCH_RADIUS or search_radius < MIN_SEARCH_RADIUS:
      return HttpResponseNotAcceptable('bad-radius')
    point = Point(float(request.GET['longitude']), float(request.GET['latitude']))
    nearbyLocations = (PlayerLocation.objects.exclude(player__state='IN')
                                                 .filter(point__distance_lte=
                                                          (point, D(km=search_radius)))
                                                 .distance(point)
                                                 .order_by('distance'))
    if 'name' in request.GET and not request.GET['name'] == '':
      toReturn = toReturn.filter(player__name__icontains=request.GET['name'])
    toReturn = [location.player for location in nearbyLocations]


    """
    Note this has to be an else if. if the player has a location and name we do something
    differente above. This is only for when we have a name and no location.
    """
  elif 'name' in request.GET and not request.GET['name'] == '':
    toReturn = toReturn.filter(name__icontains=request.GET['name'])

  toReturn = toReturn[offset:offset+max_results]
  return HttpJSONResponse(json.dumps(toReturn, cls=UDJEncoder))
