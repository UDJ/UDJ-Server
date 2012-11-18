import json
from udj.models import Player, PlayerLocation, PlayerPassword
from udj.testhelpers.tests06.testclasses import YunYoungTestCase
from udj.headers import MISSING_RESOURCE_HEADER
from udj.views.views06.auth import hashPlayerPassword

class CreatePlayerTests(YunYoungTestCase):
  def testCreatePlayer(self):
    playerName = "Yunyoung Player"
    payload = {'name' : playerName } 
    response = self.doJSONPut('/udj/0_6/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.isJSONResponse(response)
    givenPlayerId = json.loads(response.content)['id']
    addedPlayer = Player.objects.get(pk=givenPlayerId)
    self.assertEqual(addedPlayer.name, playerName)
    self.assertEqual(addedPlayer.owning_user.id, 7)
    self.assertFalse(PlayerLocation.objects.filter(player=addedPlayer).exists())
    self.assertFalse(PlayerPassword.objects.filter(player=addedPlayer).exists())


  def testCreatePasswordPlayer(self):
    playerName = "Yunyoung Player"
    password = 'playerpassword'
    passwordHash = hashPlayerPassword(password)
    payload = {'name' : playerName, 'password' : password}
    response = self.doJSONPut('/udj/0_6/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.isJSONResponse(response)
    givenPlayerId = json.loads(response.content)['id']
    addedPlayer = Player.objects.get(pk=givenPlayerId)
    self.assertEqual(addedPlayer.name, playerName)
    self.assertEqual(addedPlayer.owning_user.id, 7)
    self.assertFalse(PlayerLocation.objects.filter(player=addedPlayer).exists())

    addedPassword = PlayerPassword.objects.get(player=addedPlayer)
    self.assertEqual(addedPassword.password_hash, passwordHash)

  def testCreateLocationPlayer(self):
    playerName = "Yunyoung Player"
    payload = {'name' : playerName } 
    location = {
        'address' : '201 N Goodwin Ave',
        'locality' : 'Urbana',
        'region' : 'IL',
        'postal_code' : '61801',
        'country' : 'United States'
    }
    payload['location'] = location

    response = self.doJSONPut('/udj/0_6/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.isJSONResponse(response)
    givenPlayerId = json.loads(response.content)['id']
    addedPlayer = Player.objects.get(pk=givenPlayerId)
    self.assertEqual(addedPlayer.name, playerName)
    self.assertEqual(addedPlayer.owning_user.id, 7)
    self.assertFalse(PlayerPassword.objects.filter(player=addedPlayer).exists())

    createdLocation = PlayerLocation.objects.get(player__id=givenPlayerId)
    self.assertEqual(40.11367, createdLocation.point.y)
    self.assertEqual(-88.22401, createdLocation.point.x)
    self.assertEqual(location['address'], createdLocation.address)
    self.assertEqual(location['locality'], createdLocation.locality)
    self.assertEqual(location['region'], createdLocation.region)
    self.assertEqual(location['postal_code'], createdLocation.postal_code)
    self.assertEqual(location['country'], createdLocation.country)

  def testMultiLocationResult(self):
    playerName = "Matt Player Bitches"
    payload = {'name' : playerName } 
    location = {
        'address' : '512 S Third St',
        'locality' : 'Champaign',
        'region' : 'IL',
        'postal_code' : '61820',
        'country' : 'United States'
    }
    payload['location'] = location

    response = self.doJSONPut('/udj/0_6/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)

  def testBareLocation(self):
    playerName = "Nakey Player"
    payload = {'name' : playerName } 
    location = {
        'postal_code' : '61820',
        'country' : 'United States'
    }
    payload['location'] = location

    response = self.doJSONPut('/udj/0_6/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)

  def testBadLocation(self):
    playerName = "Yunyoung Player"
    payload = {'name' : playerName } 
    location = {
        'address' : '201 N Goodwin Ave',
        'locality' : 'Urbana',
        'region' : 'IL',
        'country' : 'United States'
    }
    payload['location'] = location

    response = self.doJSONPut('/udj/0_6/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 400)

  def testMissingSortingAlgo(self):
    playerName = "Yunyoung Player"
    payload = {'name' : playerName, 'sorting_algorithm_id' : 50}

    response = self.doJSONPut('/udj/0_6/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 404)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], "sorting_algorithm")

