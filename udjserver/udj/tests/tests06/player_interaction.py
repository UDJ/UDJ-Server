import json
import udj
from udj.models import Participant, SongSet, SongSetEntry, LibraryEntry, Player
from datetime import datetime
from udj.testhelpers.tests06.testclasses import ZachTestCase, MattTestCase, JeffTestCase, LeeTestCase, KurtisTestCase
from udj.headers import FORBIDDEN_REASON_HEADER
from udj.testhelpers.tests06.decorators import EnsureParticipationUpdated

class BeginParticipateTests(ZachTestCase):
  def testSimplePlayer(self):
    response = self.doPut('/udj/0_6/players/5/users/user')
    self.assertEqual(response.status_code, 201)
    newParticipant = Participant.objects.get(user__id=8, player__id=5)

  def testPasswordPlayerMethod(self):
    response = self.doJSONPut('/udj/0_6/players/3/users/user',
        json.dumps({'password' : 'alejandro'}))
    self.assertEqual(response.status_code, 201)
    newParticipant = Participant.objects.get(user__id=8, player__id=3)

  def testBadPassword(self):
    response = self.doJSONPut('/udj/0_6/players/3/users/user',
        json.dumps({'password' : 'wrong'}))
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['WWW-Authenticate'], 'player-password')

  def testBannedFromPlayer(self):
    response = self.doPut('/udj/0_6/players/1/users/user')
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response[FORBIDDEN_REASON_HEADER], 'banned')

  def testFullPlayer(self):
    response = self.doPut('/udj/0_6/players/7/users/user')
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response[FORBIDDEN_REASON_HEADER], 'player-full')

  @EnsureParticipationUpdated(8, 6)
  def testClearKickFlag(self):
    zach = Participant.objects.get(user__id=8, player__id=6)
    self.assertEqual(zach.kick_flag, True)
    response = self.doPut('/udj/0_6/players/6/users/user')
    self.assertEqual(response.status_code, 201)
    zach = Participant.objects.get(player__id=6, user__id=8)
    self.assertEqual(zach.kick_flag, False)

class LoginAfterLogout(LeeTestCase):
  def testLogin(self):
    response = self.doPut('/udj/0_6/players/1/users/user')
    self.assertEqual(response.status_code, 201)
    lee = Participant.objects.get(user__id=11, player__id=1)
    self.assertEqual(False, lee.logout_flag)


class GetUsersTests(MattTestCase):
  def setUp(self):
    super(GetUsersTests, self).setUp()
    matt = Participant.objects.get(user__id=9, player__id=7)
    matt.time_last_interaction = datetime.now()
    matt.save()

  @EnsureParticipationUpdated(9, 7)
  def testGetUsersSingle(self):
    response = self.doGet('/udj/0_6/players/7/users')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    users = json.loads(response.content)
    self.assertEqual(1, len(users))
    expectedIds = ['9']
    for user in users:
      self.assertTrue(user['id'] in expectedIds)

  @EnsureParticipationUpdated(9, 7)
  def testGetUsersBoth(self):
    alex = Participant.objects.get(user__id=10, player__id=7)
    alex.time_last_interaction = datetime.now()
    alex.save()
    response = self.doGet('/udj/0_6/players/7/users')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    users = json.loads(response.content)
    self.assertEqual(2, len(users))
    expectedIds = ['9', '10']
    for user in users:
      self.assertTrue(user['id'] in expectedIds)

class GetAdminsTests(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  @EnsureParticipationUpdated(3, 1)
  def testGetAdmins(self):
    response = self.doGet('/udj/0_6/players/1/admins')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    admins = json.loads(response.content)
    self.assertEqual(2, len(admins))
    expectedIds = ['1','5']
    for admin in admins:
      self.assertTrue(admin['id'] in expectedIds)

class GetSongSetTests(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  @EnsureParticipationUpdated(3, 1)
  def testGetSongSets(self):
    response = self.doGet('/udj/0_6/players/1/song_sets')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songsets = json.loads(response.content)
    self.assertEqual(2, len(songsets))
    expectedNames = ['Third Eye Blind', 'Mars Volta']
    for songset in songsets:
      self.assertTrue(songset['name'] in expectedNames)
      expectedSongs = SongSet.objects.get(name=songset['name'], player__id=1).Songs
      expectedSongIds = [x.song.lib_id for x in expectedSongs]
      self.assertTrue(len(expectedSongIds), len(songset['songs']))
      for song in songset['songs']:
        self.assertTrue(song['id'] in expectedSongIds)

class GetAvailableMusicTests(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  @EnsureParticipationUpdated(3,1)
  def testGetBasicMusic(self):
    response = self.doGet('/udj/0_6/players/1/available_music?query=Third+Eye+Blind')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(4, len(songResults))
    expectedLibIds =['1','2','3','5']
    for song in songResults:
      self.assertTrue(song['id'] in expectedLibIds)

  @EnsureParticipationUpdated(3, 1)
  def testSimpleGetWithMax(self):
    response = self.doGet('/udj/0_6/players/1/available_music?query=Third+Eye+Blind&max_results=2')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))

  @EnsureParticipationUpdated(3, 1)
  def testAlbumGet(self):
    response = self.doGet('/udj/0_6/players/1/available_music?query=Bedlam+in+Goliath')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))
    expectedLibIds =['6','7']
    for song in songResults:
      self.assertTrue(song['id'] in expectedLibIds)

class GetArtistsTests(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  @EnsureParticipationUpdated(3,1)
  def testGetArtists(self):
    response = self.doGet('/udj/0_6/players/1/available_music/artists')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    self.assertEqual(3, len(jsonResponse))
    requiredArtists = [u'Skrillex', u'The Mars Volta', u'Third Eye Blind']
    for artist in jsonResponse:
      self.assertTrue(artist in requiredArtists)

  @EnsureParticipationUpdated(3,1)
  def testSpecificArtistGet(self):
    response = self.doGet('/udj/0_6/players/1/available_music/artists/Third Eye Blind')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    self.assertEqual(4, len(jsonResponse))
    requiredIds = ['1', '2', '3', '5']
    for songId in [x['id'] for x in jsonResponse]:
      self.assertTrue(songId in requiredIds)


class GetRecentlyPlayed(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  @EnsureParticipationUpdated(3,1)
  def testRecentlyPlayed(self):
    response = self.doGet('/udj/0_6/players/1/recently_played')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    self.assertEqual(2, len(jsonResponse))
    self.assertEqual('7', jsonResponse[0]['song']['id'])
    self.assertEqual('5', jsonResponse[1]['song']['id'])

  @EnsureParticipationUpdated(3, 1)
  def testRecentlyPlayedWithMax(self):
    response = self.doGet('/udj/0_6/players/1/recently_played?max_songs=1')
    self.assertEqual(response.status_code, 200)
    jsonResponse = json.loads(response.content)
    self.assertEqual(1, len(jsonResponse))


class GetRandoms(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):

  @EnsureParticipationUpdated(3,1)
  def testSimpleGetRandom(self):
    response = self.doGet('/udj/0_6/players/1/available_music/random_songs?max_randoms=2')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    songResults = json.loads(response.content)
    self.assertEquals(2, len(songResults))
    for song in songResults:
      self.assertFalse(
          LibraryEntry.objects.get(library__id=1, lib_id=song['id']).is_deleted)
      self.assertFalse(
          LibraryEntry.objects.get(library__id=1, lib_id=song['id']).is_banned(Player.objects.get(pk=1)))

class LogoutTests(udj.testhelpers.tests06.testclasses.EnsureActiveJeffTest):
  def testLogout(self):
    response = self.doDelete('/udj/0_6/players/1/users/user')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(True, Participant.objects.get(user__id=3, player__id=1).logout_flag)
    activeUserIds = [x.user.id for x in Player.objects.get(id=1).ActiveParticipants]
    self.assertFalse(3 in activeUserIds)


class OwnerCurrentSongTestCase(udj.testhelpers.tests06.testclasses.CurrentSongTestCase):
  username="kurtis"
  userpass="testkurtis"


class AdminCurrentSongTestCase(udj.testhelpers.tests06.testclasses.CurrentSongTestCase):
  username="lucas"
  userpass="testlucas"

  def setUp(self):
    super(udj.testhelpers.tests06.testclasses.CurrentSongTestCase, self).setUp()
    lucas = Participant.objects.get(user__id=5, player__id=1)
    lucas.time_last_interaction = datetime.now()
    lucas.save()
    self.oldtime = lucas.time_last_interaction


  def tearDown(self):
    lucas = Participant.objects.get(user__id=5, player__id=1)
    self.assertTrue(lucas.time_last_interaction > self.oldtime)

class OwnerBlankCurrentSongTestCase(udj.testhelpers.tests06.testclasses.BlankCurrentSongTestCase):
  username = 'alejandro'
  userpass = 'testalejandro'

class AdminBlankCurrentSongTestCase(udj.testhelpers.tests06.testclasses.BlankCurrentSongTestCase):
  username="kurtis"
  userpass="testkurtis"

  def setUp(self):
    super(udj.testhelpers.tests06.testclasses.BlankCurrentSongTestCase, self).setUp()
    kurtis = Participant.objects.get(user__id=2, player__id=3)
    kurtis.time_last_interaction = datetime.now()
    kurtis.save()
    self.oldtime = kurtis.time_last_interaction

  def tearDown(self):
    kurtis = Participant.objects.get(user__id=2, player__id=3)
    self.assertTrue(kurtis.time_last_interaction > self.oldtime)
