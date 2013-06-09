import json
from udj.models import Player

from udj.testhelpers.tests07.testclasses import JeffTestCase

from udj.headers import NOT_ACCEPTABLE_REASON_HEADER

from settings import MIN_SEARCH_RADIUS, MAX_SEARCH_RADIUS

class GetPlayersTests(JeffTestCase):
  def testGetNearbyPlayers(self):
    response = self.doGet('/players?latitude=40.11241&longitude=-88.222053')
    self.assertGoodJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 3)
    firstPlayer = players[0]
    self.assertEqual('1', firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner']['username'])
    self.assertEqual('2', firstPlayer['owner']['id'])
    self.assertEqual(False, firstPlayer['has_password'])
    self.assertEqual(0, firstPlayer['num_active_users'])
    location = firstPlayer['location']
    self.assertEqual("201 N Goodwin", location['address'])
    self.assertEqual("Urbana", location['locality'])
    self.assertEqual("IL", location['region'])
    self.assertEqual("61801", location['postal_code'])
    self.assertEqual("US", location['country'])


  def testGetPlayersByName(self):
    response = self.doGet('/players?name=kurtis')
    self.assertGoodJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 2)
    firstPlayer = players[0]
    self.assertEqual('1', firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner']['username'])
    self.assertEqual('2', firstPlayer['owner']['id'])
    self.assertEqual(False, firstPlayer['has_password'])
    self.assertEqual(0, firstPlayer['num_active_users'])

  def testLocationSearchWithLimit(self):
    response = self.doGet('/players?latitude=40.11241&longitude=-88.222053&max_results=1')
    self.assertGoodJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)

  def testNameSearchWithLimit(self):
    response = self.doGet('/players?name=kurtis&max_results=1')
    self.assertGoodJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)

  def testSearchWithRadius(self):
    response = self.doGet('/players?latitude=40.111595&longitude=-88.204847&radius=2')
    self.assertGoodJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(2, len(players))

  def testSearchWithRadiusAndLimit(self):
    response = self.doGet('/players?latitude=40.111595&longitude=-88.204847&radius=2&max_results=1')
    self.assertGoodJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(1, len(players))
    self.assertEqual('6', players[0]["id"])

  def testSearchWithRadiusLimitAndOffset(self):
    response = self.doGet('/players?latitude=40.111595&longitude=-88.204847&radius=2&max_results=1&start_position=1')
    self.assertGoodJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(1, len(players))
    self.assertEqual('1', players[0]["id"])

  def testTooSmallRadius(self):
    badRadius = MIN_SEARCH_RADIUS -1
    response = self.doGet('/players?latitude=40.11241&longitude=-88.222053&radius=%d' % badRadius)
    self.assertEqual(406, response.status_code)
    self.assertEqual('bad-radius', response[NOT_ACCEPTABLE_REASON_HEADER])

  def testTooBigRadius(self):
    badRadius = MAX_SEARCH_RADIUS +1
    response = self.doGet('/players?latitude=40.11381&longitude=-88.224083&radius=%d' % badRadius)
    self.assertEqual(406, response.status_code)
