import json

from udj.tests.testhelpers import JeffTestCase
from udj.tests.testhelpers import YunYoungTestCase
from udj.tests.testhelpers import KurtisTestCase
from udj.tests.testhelpers import AlejandroTestCase
from udj.tests.testhelpers import EnsureParticipationUpdated
from udj.models import Vote
from udj.models import LibraryEntry
from udj.models import Player
from udj.models import PlayerLocation
from udj.models import PlayerPassword
from udj.models import Participant
from udj.models import ActivePlaylistEntry
from udj.models import PlaylistEntryTimePlayed
from udj.auth import hashPlayerPassword
from udj.headers import DJANGO_PLAYER_PASSWORD_HEADER

from django.test.client import Client

from datetime import datetime



class GetPlayersTests(JeffTestCase):
  def testGetNearbyPlayers(self):
    response = self.doGet('/udj/players/40.11241/-88.222053')
    self.assertEqual(response.status_code, 200, response.content)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)
    firstPlayer = players[0]
    self.assertEqual(1, firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner_username'])
    self.assertEqual(2, firstPlayer['owner_id'])
    self.assertEqual(False, firstPlayer['has_password'])

  def testGetPlayersByName(self):
    response = self.doGet('/udj/players?name=kurtis')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    players = json.loads(response.content)
    self.assertEqual(len(players), 1)
    firstPlayer = players[0]
    self.assertEqual(1, firstPlayer['id'])
    self.assertEqual("Kurtis Player", firstPlayer['name'])
    self.assertEqual("kurtis", firstPlayer['owner_username'])
    self.assertEqual(2, firstPlayer['owner_id'])
    self.assertEqual(False, firstPlayer['has_password'])

class CreatePlayerTest(YunYoungTestCase):
  def testCreatePlayer(self):
    playerName = "Yunyoung Player"
    payload = {'name' : playerName } 
    response = self.doJSONPut('/udj/users/7/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.isJSONResponse(response)
    givenPlayerId = json.loads(response.content)['player_id']
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
    response = self.doJSONPut('/udj/users/7/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.isJSONResponse(response)
    givenPlayerId = json.loads(response.content)['player_id']
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
        'city' : 'Urbana',
        'state' : 'IL',
        'zipcode' : 61801
    }
    payload['location'] = location

    response = self.doJSONPut('/udj/users/7/players/player', json.dumps(payload))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.isJSONResponse(response)
    givenPlayerId = json.loads(response.content)['player_id']
    addedPlayer = Player.objects.get(pk=givenPlayerId)
    self.assertEqual(addedPlayer.name, playerName)
    self.assertEqual(addedPlayer.owning_user.id, 7)
    self.assertFalse(PlayerPassword.objects.filter(player=addedPlayer).exists())

    createdLocation = PlayerLocation.objects.get(player__id=givenPlayerId)
    self.assertEqual(createdLocation.address, location['address'])
    self.assertEqual(createdLocation.city, location['city'])
    self.assertEqual(createdLocation.state.name, location['state'])
    self.assertEqual(createdLocation.zipcode, location['zipcode'])
    self.assertEqual(createdLocation.latitude, 40.1135372574038)
    self.assertEqual(createdLocation.longitude, -88.2240781569526)


class PlayerModificationTests(KurtisTestCase):

  def testChangeName(self):
    newName = "A Bitchn' name"
    response = self.doPost('/udj/users/2/players/1/name', {'name': newName})
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    player = Player.objects.get(pk=1)
    self.assertEqual(player.name, newName)

  def testSetPassword(self):
    newPassword = 'nudepassword'
    response = self.doPost('/udj/users/2/players/1/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.get(player__id=1)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))

  def testSetLocation(self):
    newLocation = {
      'address' : '305 Vicksburg Lane',
      'city' : 'Plymouth',
      'state' : 'MN',
      'zipcode' : 55447
    }

    response = self.doPost('/udj/users/2/players/1/location', newLocation)
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerLocation = PlayerLocation.objects.get(player__id=1)
    self.assertEqual(playerLocation.address, '305 Vicksburg Lane')
    self.assertEqual(playerLocation.city, 'Plymouth')
    self.assertEqual(playerLocation.state.id, 23)
    self.assertEqual(playerLocation.zipcode, 55447)


class PlayerModificationTests2(AlejandroTestCase):

  def testChangePassword(self):
    oldTime = PlayerPassword.objects.get(player__id=3).time_set
    newPassword = "nudepassword"
    response = self.doPost('/udj/users/6/players/3/password', {'password': newPassword})
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.get(player__id=3)
    self.assertEqual(playerPassword.password_hash, hashPlayerPassword(newPassword))
    self.assertTrue(oldTime < playerPassword.time_set)

  def testDeletePassword(self):
    response = self.doDelete('/udj/users/6/players/3/password')
    self.assertEqual(response.status_code, 200, "Error: " + response.content)
    playerPassword = PlayerPassword.objects.filter(player__id=3)
    self.assertFalse(playerPassword.exists())

class BeginParticipateTests(YunYoungTestCase):
  def testSimplePlayer(self):
    response = self.doPut('/udj/players/1/users/7')
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    newParticipant = Participant.objects.get(user__id=7, player__id=1)

  def testPasswordPlayer(self):
    response = self.doPut('/udj/players/3/users/7', 
        headers={DJANGO_PLAYER_PASSWORD_HEADER : 'alejandro'})
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    newParticipant = Participant.objects.get(user__id=7, player__id=3)

  def testBadPassword(self):
    response = self.doPut('/udj/players/3/users/7', 
        headers={DJANGO_PLAYER_PASSWORD_HEADER : 'wrong password'})
    self.assertEqual(response.status_code, 401, "Error: " + response.content)
    self.assertEqual(response['WWW-Authenticate'], 'player-password')
    newParticipant = Participant.objects.filter(user__id=7, player__id=3)
    self.assertFalse(newParticipant.exists())

  def testBadNoPassword(self):
    response = self.doPut('/udj/players/3/users/7')
    self.assertEqual(response.status_code, 401, "Error: " + response.content)
    self.assertEqual(response['WWW-Authenticate'], 'player-password')
    newParticipant = Participant.objects.filter(user__id=7, player__id=3)
    self.assertFalse(newParticipant.exists())

class PlayerAdminTests(KurtisTestCase):

  def testGetUsers(self):
    participants = Participant.objects.filter(player__id=1).exclude(user__id=7)
    participants.update(time_last_interaction=datetime.now())

    response = self.doGet('/udj/players/1/users')
    self.assertEqual(response.status_code, 200)
    jsonUsers = json.loads(response.content)
    self.assertEquals(len(jsonUsers), 2)
    possibleUsers = ['jeff', 'vilas']
    for user in jsonUsers:
      self.assertTrue(user['username'] in possibleUsers)

  def testGetUsers2(self):
    participants = Participant.objects.filter(player__id=1)
    participants.update(time_last_interaction=datetime.now())

    response = self.doGet('/udj/players/1/users')
    self.assertEqual(response.status_code, 200)
    jsonUsers = json.loads(response.content)
    self.assertEquals(len(jsonUsers), 3)
    possibleUsers = ['jeff', 'vilas', 'yunyoung']
    for user in jsonUsers:
      self.assertTrue(user['username'] in possibleUsers)

  def testSetCurrentSong(self):
    response = self.doPost('/udj/players/1/current_song', {'lib_id' : 1})
    self.assertEqual(response.status_code, 200, response.content)

    self.assertEqual('FN',ActivePlaylistEntry.objects.get(pk=5).state)
    self.assertEqual('PL',ActivePlaylistEntry.objects.get(pk=1).state)
    PlaylistEntryTimePlayed.objects.get(playlist_entry__id=1)

  def testSetPaused(self):
    response = self.doPost('/udj/users/2/players/1/state', {'state': 'paused'})
    response = self.assertEqual(response.status_code, 200)

    self.assertEqual(Player.objects.get(pk=1).state, 'PA')

  def testSetInactive(self):
    response = self.doPost('/udj/users/2/players/1/state', {'state': 'inactive'})
    response = self.assertEqual(response.status_code, 200)

    self.assertEqual(Player.objects.get(pk=1).state, 'IN')

  def testSetPlaying(self):
    response = self.doPost('/udj/users/2/players/1/state', {'state': 'playing'})
    response = self.assertEqual(response.status_code, 200)

    self.assertEqual(Player.objects.get(pk=1).state, 'PL')

  def testBadStateRequest(self):
    response = self.doPost('/udj/users/2/players/1/state', {'state': 'wrong'})
    response = self.assertEqual(response.status_code, 400)

    self.assertEqual(Player.objects.get(pk=1).state, 'PL')

  def testSetVolume(self):
    response = self.doPost('/udj/users/2/players/1/volume', {'volume': '1'})
    response = self.assertEqual(response.status_code, 200)

    self.assertEqual(Player.objects.get(pk=1).volume, 1)

  def testBadSetVolume(self):
    response = self.doPost('/udj/users/2/players/1/volume', {'volume': 'a'})
    response = self.assertEqual(response.status_code, 400)

    self.assertEqual(Player.objects.get(pk=1).volume, 5)

  def testBadSetVolume2(self):
    response = self.doPost('/udj/users/2/players/1/volume', {'volume': '11'})
    response = self.assertEqual(response.status_code, 400)

    self.assertEqual(Player.objects.get(pk=1).volume, 5)



class PlayerAdminTests2(AlejandroTestCase):
  def testSetCurrentSongWithBlank(self):
    response = self.doPost('/udj/players/3/current_song', {'lib_id' : 1})
    self.assertEqual(response.status_code, 200, response.content)

    self.assertEqual('PL',ActivePlaylistEntry.objects.get(pk=8).state)
    PlaylistEntryTimePlayed.objects.get(playlist_entry__id=8)

  def testGetPlaylistWithBlankCurrent(self):
    response = self.doGet('/udj/players/3/active_playlist')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    current_song = jsonResponse['current_song']
    self.assertEqual(current_song,{})
    plSongs = ActivePlaylistEntry.objects.filter(song__player__id=3, state='QE')
    plSongIds = [x.song.player_lib_song_id for x in plSongs]
    for plSong in jsonResponse['active_playlist']:
      self.assertTrue(plSong['song']['id'] in plSongIds)
    self.assertEqual(len(jsonResponse['active_playlist']), len(plSongIds))



class PlayerQueryTests(YunYoungTestCase):

  @EnsureParticipationUpdated(7, 1)
  def testGetUsers(self):
    otherUsers = Participant.objects.filter(player__id=1).exclude(user__id=7)
    otherUsers.update(time_last_interaction=datetime.now())
    response = self.doGet('/udj/players/1/users')
    self.assertEqual(response.status_code, 200)
    jsonUsers = json.loads(response.content)
    self.assertEquals(len(jsonUsers), 3)
    possibleUsers = ['jeff', 'vilas', 'yunyoung']
    for user in jsonUsers:
      self.assertTrue(user['username'] in possibleUsers)

  def testBadGetUsers(self):
    response = self.doGet('/udj/players/1/users')
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['WWW-Authenticate'], 'begin-participating')

  @EnsureParticipationUpdated(7, 1)
  def testSimpleGetMusic(self):

    response = self.doGet('/udj/players/1/available_music?query=Third+Eye+Blind')
    self.assertEqual(response.status_code, 200)
    songResults = json.loads(response.content)
    self.assertEquals(4, len(songResults))
    expectedLibIds =[1,2,3,5]
    for song in songResults:
      self.assertTrue(song['id'] in expectedLibIds)

  @EnsureParticipationUpdated(7, 1)
  def testAlbumGet(self):

    response = self.doGet('/udj/players/1/available_music?query=Bedlam+in+Goliath')
    self.assertEqual(response.status_code, 200)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))
    expectedLibIds =[6,7]
    for song in songResults:
      self.assertTrue(song['id'] in expectedLibIds)

  @EnsureParticipationUpdated(7, 1)
  def testGetRandom(self):

    response = self.doGet('/udj/players/1/available_music/random_songs?max_randoms=2')
    self.assertEqual(response.status_code, 200)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))
    for song in songResults:
      self.assertFalse(
          LibraryEntry.objects.get(player__id=1, player_lib_song_id=song['id']).is_deleted)
      self.assertFalse(
          LibraryEntry.objects.get(player__id=1, player_lib_song_id=song['id']).is_banned)

  @EnsureParticipationUpdated(7, 1)
  def testGetPlaylist(self):

    response = self.doGet('/udj/players/1/active_playlist')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    current_song = jsonResponse['current_song']
    realCurrentSong = ActivePlaylistEntry.objects.get(song__player__id=1, state='PL')
    self.assertEqual(current_song['song']['id'], realCurrentSong.song.player_lib_song_id)
    plSongs = ActivePlaylistEntry.objects.filter(song__player__id=1, state='QE')
    plSongIds = [x.song.player_lib_song_id for x in plSongs]
    for plSong in jsonResponse['active_playlist']:
      self.assertTrue(plSong['song']['id'] in plSongIds)
    self.assertEqual(len(jsonResponse['active_playlist']), len(plSongIds))


class PlaylistModTests(JeffTestCase):

  @EnsureParticipationUpdated(3, 1)
  def testSimpleAdd(self):

    response = self.doPut('/udj/players/1/active_playlist/songs/9')
    self.assertEqual(response.status_code, 201)

    added = ActivePlaylistEntry.objects.get(
      song__player__id=1, song__player_lib_song_id=9, state='QE')
    vote = Vote.objects.get(playlist_entry=added)

  @EnsureParticipationUpdated(3, 1)
  def testAddRemovedSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/10')
    self.assertEqual(response.status_code, 201)

    added = ActivePlaylistEntry.objects.get(
      song__player__id=1, song__player_lib_song_id=10, state='QE')
    vote = Vote.objects.get(playlist_entry=added)

  @EnsureParticipationUpdated(3, 1)
  def testAddBannedSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/4')
    self.assertEqual(response.status_code, 404)

    self.assertFalse( ActivePlaylistEntry.objects.filter(
      song__player__id=1, song__player_lib_song_id=4, state='QE').exists())

  @EnsureParticipationUpdated(3, 1)
  def testAddDeletedSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/8')
    self.assertEqual(response.status_code, 404)

    self.assertFalse( ActivePlaylistEntry.objects.filter(
      song__player__id=1, song__player_lib_song_id=8, state='QE').exists())

  @EnsureParticipationUpdated(3, 1)
  def testAddQueuedSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/1')
    self.assertEqual(response.status_code, 409)

  @EnsureParticipationUpdated(3, 1)
  def testAddPlayingSong(self):
    response = self.doPut('/udj/players/1/active_playlist/songs/6')
    self.assertEqual(response.status_code, 409)





"""
import json
from django.contrib.auth.models import User
from udj.tests.testhelpers import User2TestCase
from udj.tests.testhelpers import User3TestCase
from udj.tests.testhelpers import User4TestCase
from udj.tests.testhelpers import User5TestCase
from udj.tests.testhelpers import User8TestCase
from udj.models import EventPassword
from udj.models import Event
from udj.models import EventEndTime
from udj.models import LibraryEntry
from udj.models import Ticket
from udj.models import EventGoer
from udj.models import ActivePlaylistEntry
from udj.models import AvailableSong
from decimal import Decimal
from datetime import datetime
from udj.headers import getGoneResourceHeader, getDjangoUUIDHeader, getDjangoEventPasswordHeader

class GetEventsTest(User5TestCase):
  def testGetNearbyEvents(self):
    #TODO This needs to be more robust, however the location functionality
    # isn't fully working just yet
    response = self.doGet('/udj/events/40.11381/-88.224083')
    self.assertEqual(response.status_code, 200)
    self.verifyJSONResponse(response)
    events = json.loads(response.content)
    self.assertEqual(len(events), 2)

  def testGetEvents(self):
    response = self.doGet('/udj/events?name=empty')
    self.assertEqual(response.status_code, 200)
    self.verifyJSONResponse(response)
    events = json.loads(response.content)
    self.assertEqual(len(events), 1)
    emptyEvent = events[0]
    self.assertEqual(int(emptyEvent['id']), 3)
    self.assertEqual(emptyEvent['longitude'], -88.224006)
    self.assertEqual(emptyEvent['latitude'], 40.113523)
    self.assertEqual(int(emptyEvent['host_id']), 4)
    self.assertEqual(emptyEvent['host_username'], 'test4')
    self.assertEqual(emptyEvent['has_password'], False)

class CreateEventTest(User5TestCase):
  def testCreateEvent(self):
    partyName = "A Bitchn' Party"
    event = {'name' : partyName } 
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.verifyJSONResponse(response)
    givenEventId = json.loads(response.content)['event_id']
    addedEvent = Event.objects.get(pk=givenEventId)
    self.assertEqual(addedEvent.name, partyName)
    partyHost = EventGoer.objects.get(event=addedEvent, user__id=self.user_id)

  def testCreatePasswordEvent(self):
    eventName = "A Bitchn' Party"
    eventPassword = 'dog'
    event = {
      'name' : eventName,
      'password' : eventPassword
    }
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    self.verifyJSONResponse(response)
    givenEventId = json.loads(response.content)['event_id']
    addedEvent = Event.objects.get(pk=givenEventId)
    self.assertEqual(addedEvent.name, eventName)
    partyHost = EventGoer.objects.get(event=addedEvent, user__id=self.user_id)
    password = EventPassword.objects.get(event__id=givenEventId)




class EndEventTest(User2TestCase):
  def testEndEvent(self):
    response = self.doDelete('/udj/events/2')
    self.assertEqual(Event.objects.get(pk=2).state,u'FN')
    EventEndTime.objects.get(event__id=2)
    EventGoer.objects.get(user__id=2, event__id=2, state=u'LE')

  def testDoubleEnd(self):
    response = self.doDelete('/udj/events/2')
    response = self.doDelete('/udj/events/2')

class EndEmptyEventTest(User4TestCase):
  def testEndEmptyEvent(self):
    response = self.doDelete('/udj/events/3')
    self.assertEqual(Event.objects.get(pk=3).state,u'FN')
    EventGoer.objects.get(user__id=4, event__id=3, state=u'LE')


class JoinEventTest(User5TestCase):
  def testJoinEvent(self):
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201, "Error: " + response.content)
    inevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'IE')

  def testDoubleJoinEvent(self):
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201)
    inevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'IE')
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201)
    inevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'IE')

  def testJoinLeaveJoinEvent(self):
    response = self.doPut('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 201)
    inevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'IE')
    response = self.doDelete('/udj/events/2/users/5')
    self.assertEqual(response.status_code, 200)
    leftevent_goer = EventGoer.objects.get(
      event__id=2, user__id=5, state=u'LE')
    response = self.doPut('/udj/events/4/users/5')
    self.assertEqual(response.status_code, 201)
    inevent_goer = EventGoer.objects.get(
      event__id=4, user__id=5, state=u'IE')

  def testJoinEndedEvent(self):
    response = self.doPut('/udj/events/1/users/5')
    self.assertEqual(response.status_code, 410)
    self.assertEqual(response[getGoneResourceHeader()], "event")
    shouldntBeThere = EventGoer.objects.filter(event__id=1, user__id=5)
    self.assertFalse(shouldntBeThere.exists())

  def testPassword(self):
    response = self.doPut(
      '/udj/events/6/users/5',
      headers={getDjangoEventPasswordHeader() : 'udj'})
    self.assertEqual(response.status_code, 201, response.content)

  def testBadPassword(self):
    response = self.doPut(
      '/udj/events/6/users/5',
      headers={getDjangoEventPasswordHeader() : 'wrong'})
    self.assertEqual(response.status_code, 404, response.content)


class LeaveEventTest(User3TestCase):
  def testLeaveEvent(self):
    response = self.doDelete('/udj/events/2/users/3')
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.get(
      event__id=2, user__id=3, state=u'LE')

class LeaveEndedEventTest(User8TestCase):
  def testLeaveEndedEvent(self):
    response = self.doDelete('/udj/events/1/users/8')
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.get(
      event__id=1, user__id=8, state=u'LE')


#Disabling this for now. We'll come back to it later.
class KickUserTest(User2TestCase):
  def testKickUser(self):
    userId=4
    response = self.doDelete('/udj/events/1/users/'+str(userId))
    self.assertEqual(response.status_code, 200, response.content)
    event_goer_entries = EventGoer.objects.filter(event__id=1, user__id=userId)
    self.assertEqual(len(event_goer_entries), 0)

class TestGetAvailableMusic(User3TestCase):
  def verifyExpectedResults(self, results, realSongs):
    realIds = [song.song.host_lib_song_id for song in realSongs]
    for song in results:
      self.assertTrue(song['id'] in realIds)
 
  def testGetAlbum(self): 
    response = self.doGet('/udj/events/2/available_music?query=blue')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 2)
    realSongs = AvailableSong.objects.filter(song__album="Blue")
    self.verifyExpectedResults(results, realSongs)

  def testMaxResults(self): 
    response = self.doGet(
      '/udj/events/2/available_music?query=blue&max_results=1')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
 
  def testGetArtist(self): 
    response = self.doGet(
      '/udj/events/2/available_music?query=third+eye+blind')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 3)
    realSongs = AvailableSong.objects.filter(song__artist="Third Eye Blind")
    self.verifyExpectedResults(results, realSongs)

  def testGetTitle(self):
    response = self.doGet(
      '/udj/events/2/available_music?query=Never+Let+You+Go')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
    realSongs = AvailableSong.objects.filter(song__title="Never Let You Go")
    self.verifyExpectedResults(results, realSongs)

  def testSongNotAvailable(self): 
    response = self.doGet(
      '/udj/events/2/available_music?query=water+landing')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 0)

  def testSongsDontExist(self): 
    response = self.doGet(
      '/udj/events/2/available_music?query=smashing+pumpkins')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 0)

  def testGetRandoms(self):
    response = self.doGet(
      '/udj/events/2/available_music/random_songs')
    self.assertEqual(response.status_code, 200, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)

  def testBlankSearch(self):
    response = self.doGet(
      '/udj/events/2/available_music?query=')
    self.assertEqual(response.status_code, 400, response.content)

class TestPutAvailableMusic(User2TestCase):
  def testSimplePut(self): 
    toAdd=[6]
    response = self.doJSONPut(
      '/udj/events/2/available_music', json.dumps(toAdd),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 201, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0], 6)
    AvailableSong.objects.get(
      song__host_lib_song_id=6, song__owning_user__id=2)

  def testMultiPut(self):
    toAdd = [6,7]
    response = self.doJSONPut(
      '/udj/events/2/available_music', json.dumps(toAdd),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 201, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 2)
    self.assertTrue(6 in results)
    self.assertTrue(7 in results)
    AvailableSong.objects.get(
      song__host_lib_song_id=6, song__owning_user__id=2)
    AvailableSong.objects.get(
      song__host_lib_song_id=7, song__owning_user__id=2)

  def testDoublePut(self):
    toAdd = [8]
    response = self.doJSONPut(
      '/udj/events/2/available_music', json.dumps(toAdd),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 201, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 1)
    self.assertTrue(8 in results)
    AvailableSong.objects.get(
      song__host_lib_song_id=8, song__owning_user__id=2)

    toAdd = [7, 8]
    response = self.doJSONPut(
      '/udj/events/2/available_music', json.dumps(toAdd),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    self.assertEqual(response.status_code, 201, response.content)
    self.verifyJSONResponse(response)
    results = json.loads(response.content)
    self.assertEqual(len(results), 2)
    self.assertTrue(7 in results)
    self.assertTrue(8 in results)
    AvailableSong.objects.get(
      song__host_lib_song_id=7, song__owning_user__id=2)
    AvailableSong.objects.get(
      song__host_lib_song_id=8, song__owning_user__id=2)

  def testReaddDeleted(self):
    toAdd = [11]
    response = self.doJSONPut(
      '/udj/events/2/available_music', json.dumps(toAdd),
      headers={getDjangoUUIDHeader() : "20000000000000000000000000000000"})
    readdedSong = AvailableSong.objects.get(
      song__host_lib_song_id=11, event__id=2)
    self.assertTrue(readdedSong.state, u'AC')

class TestCantPutAvailableMusic(User3TestCase):
  def testPut(self):
   toAdd=[7]
   response = self.doJSONPut('/udj/events/2/available_music', json.dumps(toAdd))
   self.assertEqual(response.status_code, 403, response.content)

class TestDeleteAvailableMusic(User2TestCase):
  def testRemove(self):
    response = self.doDelete('/udj/events/2/available_music/3')
    self.assertEqual(response.status_code, 200, response.content)
    foundSongs = AvailableSong.objects.get(
      song__host_lib_song_id=3, song__owning_user__id=2)
    self.assertTrue(foundSongs.state, 'RM')
    shouldBeRemoved = ActivePlaylistEntry.objects.get(pk=4)
    self.assertTrue(shouldBeRemoved.state, u'RM')

  def testBadRemove(self):
    response = self.doDelete('/udj/events/2/available_music/400')
    self.assertEqual(response.status_code, 404, response.content)

  def testRemoveSongAlsoUsedInPreviousEvent(self):
    response = self.doDelete('/udj/events/2/available_music/1')
    self.assertEqual(response.status_code, 200, response.content)
    foundSongs = AvailableSong.objects.get(
      song__host_lib_song_id=1, event__id=2)
    self.assertTrue(foundSongs.state, 'RM')



class TestSetCurrentSong(User2TestCase):
  def testSetCurrentSong(self):
    response = self.doPost(
      '/udj/events/2/current_song', 
      {'playlist_entry_id' : '4'})
    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(ActivePlaylistEntry.objects.get(pk=4).state, u'PL')
    self.assertEqual(ActivePlaylistEntry.objects.get(pk=5).state, u'FN')

  def testSetWithNoCurrentSong(self):
    currentSong = ActivePlaylistEntry.objects.get(pk=5)
    currentSong.state = u'FN'
    currentSong.save()
    response = self.doPost(
      '/udj/events/2/current_song',
      {'playlist_entry_id' : '4'})
    self.assertEqual(response.status_code, 200, response.content)
    self.assertEqual(ActivePlaylistEntry.objects.get(pk=4).state, u'PL')

class TestDuplicateHostEventCreate(User2TestCase):
  def testDuplicatHostEventCreate(self):
    partyName = "A Bitchn' Party"
    event = {'name' : partyName }
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 409)

class TestDoubleEventCreate(User5TestCase):
  def testDoubleEventCreate(self):
    partyName = "A Bitchn' Party"
    event = {'name' : partyName } 
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201)
    self.verifyJSONResponse(response)
    eventId = json.loads(response.content)['event_id']
    response = self.doDelete('/udj/events/'+str(eventId))
    self.assertEqual(response.status_code, 200)
    response = self.doJSONPut('/udj/events/event', json.dumps(event))
    self.assertEqual(response.status_code, 201)
    self.verifyJSONResponse(response)
    eventId = json.loads(response.content)['event_id']
    response = self.doDelete('/udj/events/'+str(eventId))

class TestGetEventGoers(User3TestCase):
  def testRegularGetEventGoers(self):
    event_id = 2
    response = self.doGet('/udj/events/' + str(event_id) + '/users')
    self.assertEqual(response.status_code, 200)
    self.verifyJSONResponse(response)
    eventGoersJson = json.loads(response.content)
    eventGoers = EventGoer.objects.filter(event__id=event_id)
    self.assertEqual(len(eventGoersJson), len(eventGoers))
    jsonIds = [eg['id'] for eg in eventGoersJson]
    for eg in eventGoers:
      self.assertTrue(eg.user.id in jsonIds)
"""
