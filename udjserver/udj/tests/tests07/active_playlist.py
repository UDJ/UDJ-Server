import json

import udj
from udj.models import (Player,
                        PlayerPermissionGroup,
                        PlayerPermission,
                        LibraryEntry,
                        ActivePlaylistEntry,
                        Participant,
                        Vote,
                        SortingAlgorithm)
from udj.testhelpers.tests07.decorators import EnsureParticipationUpdated
from udj.headers import MISSING_RESOURCE_HEADER
from udj.testhelpers.tests07.testclasses import KurtisTestCase

from datetime import datetime

class GetActivePlaylistTests(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid=1

  @EnsureParticipationUpdated(3,1)
  def testGetPlaylist(self):
    response = self.doGet('/players/1/active_playlist')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    current_song = jsonResponse['current_song']
    realCurrentSong = ActivePlaylistEntry.objects.get(song__library__id=1, state='PL')
    self.assertEqual(current_song['song']['id'], realCurrentSong.song.lib_id)
    plSongs = ActivePlaylistEntry.objects.filter(song__library__id=1, state='QE')
    plSongIds = [x.song.lib_id for x in plSongs]
    for plSong in jsonResponse['active_playlist']:
      self.assertTrue(plSong['song']['id'] in plSongIds)
    self.assertEqual(len(jsonResponse['active_playlist']), len(plSongIds))

    self.assertEqual(jsonResponse['volume'], 5)
    self.assertEqual(jsonResponse['state'], 'playing')

  def testRoundRobin(self):
    kurtisPlayer = Player.objects.get(pk=1)
    roundRobin = SortingAlgorithm.objects.get(pk=3)

    kurtisPlayer.sorting_algo = roundRobin
    kurtisPlayer.save()

    response = self.doGet('/players/1/active_playlist')
    self.assertEqual(response.status_code, 200)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)


class PlaylistModTests(KurtisTestCase):
  def testBasicSongRemove(self):
    response = self.doDelete('/players/1/active_playlist/songs/1/2')
    self.assertEqual(response.status_code, 200)

    shouldBeRemoved = ActivePlaylistEntry.objects.get(pk=2)
    self.assertEqual('RM', shouldBeRemoved.state)

  def testPlaylistMultiMod(self):
    toAdd = [{'id' : '9', 'library_id' : '1'}]
    toRemove = [{'id' : '3', 'library_id' : '1'}]

    response = self.doJSONPost(
      '/players/1/active_playlist',
      {'to_add' : toAdd, 'to_remove' : toRemove}
    )
    self.assertEqual(response.status_code, 200, response.content)
    #make sure song was queued
    addedSong = ActivePlaylistEntry.objects.get(
      player__id=1, song__lib_id='9', song__library__id=1, state='QE')
    #make sure song was removed
    self.assertFalse(ActivePlaylistEntry.objects.filter(
      player__id=1,
      song__lib_id='3',
      song__library__id=1,
      state='QE').exists())
    self.assertTrue(ActivePlaylistEntry.objects.filter(
      player__id=1,
      song__lib_id='3',
      song__library__id=1,
      state='RM').exists())

  def testBadRemoveMultiMod(self):
    toAdd = [{'id' : '9', 'library_id' : '1'}]
    toRemove = [{'id' : '3', 'library_id' : '1'}, {'id' : '6', 'library_id' : '1'}]

    response = self.doJSONPost(
      '/players/1/active_playlist',
      {'to_add' : toAdd, 'to_remove' : toRemove}
    )
    self.assertEqual(response.status_code, 404, response.content)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')

    responseJSON = json.loads(response.content)
    self.assertEqual([{'id' : '6', 'library_id' : '1'}], responseJSON)

    #ensure 9 wasn't added
    self.assertFalse(ActivePlaylistEntry.objects.filter(
      player__id='1',
      song__lib_id='9',
      song__library=1,
      state="QE").exists())

    #ensure 3 is still queued
    ActivePlaylistEntry.objects.get(
      player__id='1',
      song__lib_id='3',
      song__library__id=1,
      state="QE")

  def testDuplicateAddMultiMod(self):
    sixInitVoteCount = len(ActivePlaylistEntry.objects.get(player__id=1,
                                                           song__library__id=1,
                                                           song__lib_id=6).Upvoters)

    toAdd = [{'id' : '9', 'library_id' : '1'}, {'id' : '6', 'library_id' : '1'}]
    toRemove = [{'id' : '3', 'library_id' : '1'}]
    response = self.doJSONPost(
      '/players/1/active_playlist',
      {'to_add' : toAdd, 'to_remove' : toRemove}
    )
    self.assertEqual(200, response.status_code, response.content)

    #ensure 9 was added
    self.assertTrue(ActivePlaylistEntry.objects.filter(
      song__library__id='1',
      song__lib_id='9',
      player=1,
      state="QE").exists())

    #ensure 3 is no longer queued
    ActivePlaylistEntry.objects.get(
      song__library__id=1,
      song__lib_id='3',
      player=1,
      state="RM")

    #ensure the vote count for 6 hasn't changed since it's the current song.
    sixNewVoteCount = len(ActivePlaylistEntry.objects.get(player__id=1, 
                                                          song__lib_id=6,
                                                          song__library__id=1).Upvoters)
    self.assertEqual(sixInitVoteCount, sixNewVoteCount)




class ParticipantPlaylistModTests(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid=1

  @EnsureParticipationUpdated(3, 1)
  def testSimpleAdd(self):

    response = self.doPut('/players/1/active_playlist/songs/1/9')
    self.assertEqual(response.status_code, 201)

    added = ActivePlaylistEntry.objects.get(
      song__library__id=1, song__lib_id=9, state='QE')
    vote = Vote.objects.get(playlist_entry=added)

  @EnsureParticipationUpdated(3, 1)
  def testAddRemovedSong(self):
    response = self.doPut('/players/1/active_playlist/songs/1/10')
    self.assertEqual(response.status_code, 201)

    added = ActivePlaylistEntry.objects.get(
      song__library__id=1, song__lib_id=u'10', state='QE')
    vote = Vote.objects.get(playlist_entry=added)

  @EnsureParticipationUpdated(3, 1)
  def testAddBannedSong(self):
    response = self.doPut('/players/1/active_playlist/songs/1/4')
    self.assertEqual(response.status_code, 404)

    self.assertFalse( ActivePlaylistEntry.objects.filter(
      song__library__id=1, song__lib_id=4, state='QE').exists())

  @EnsureParticipationUpdated(3, 1)
  def testAddDeletedSong(self):
    response = self.doPut('/players/1/active_playlist/songs/1/8')
    self.assertEqual(response.status_code, 404)

    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__library__id=1, song__lib_id=8, state='QE').exists())

  @EnsureParticipationUpdated(3, 1)
  def testAddQueuedSong(self):
    initialUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).Upvoters)
    response = self.doPut('/players/1/active_playlist/songs/1/1')
    self.assertEqual(response.status_code, 200)
    afterUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).Upvoters)
    self.assertEqual(initialUpvoteCount+1, afterUpvoteCount)


  @EnsureParticipationUpdated(3, 1)
  def testAddPlayingSong(self):
    initialUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=6).Upvoters)
    response = self.doPut('/players/1/active_playlist/songs/1/6')
    self.assertEqual(response.status_code, 200)
    afterUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=6).Upvoters)
    self.assertEqual(initialUpvoteCount, afterUpvoteCount)

  @EnsureParticipationUpdated(3, 1)
  def testRemoveQueuedSongWithoutPermission(self):
    response = self.doDelete('/players/1/active_playlist/songs/1/3')
    self.assertBadPlayerPermission(response)

    removedSong = ActivePlaylistEntry.objects.get(pk=3)
    self.assertEqual('QE', removedSong.state)

    toAdd = []
    toRemove = [{'id' : '3', 'library_id' : '1'}]

    response = self.doJSONPost(
      '/players/1/active_playlist',
      {'to_add' : toAdd, 'to_remove' : toRemove}
    )
    self.assertBadPlayerPermission(response)
    removedSong = ActivePlaylistEntry.objects.get(pk=3)
    self.assertEqual('QE', removedSong.state)


  @EnsureParticipationUpdated(3, 1)
  def testAddSongWithoutPermission(self):
    PlayerPermission(player=Player.objects.get(pk=1), 
                     permission="APA",
                     group=PlayerPermissionGroup.objects.get(pk=1)).save()
    response = self.doPut('/players/1/active_playlist/songs/1/9')
    self.assertBadPlayerPermission(response)

    should_not_exists = ActivePlaylistEntry.objects.filter(song__lib_id=u'9', song__library__id=9)
    self.assertFalse(should_not_exists.exists())

    toAdd = [{'id' : '9', 'library_id' : '1'}]
    toRemove = []

    response = self.doJSONPost(
      '/players/1/active_playlist',
      {'to_add' : toAdd, 'to_remove' : toRemove}
    )
    self.assertBadPlayerPermission(response)

    should_not_exists = ActivePlaylistEntry.objects.filter(song__lib_id=u'9', song__library__id=9)
    self.assertFalse(should_not_exists.exists())



  @EnsureParticipationUpdated(3,1)
  def testMultiAdd(self):
    toAdd = [{"library_id" : "1" , "id" : "9"},{"library_id" : "1", "id" : "10"}]
    toRemove = []

    response = self.doJSONPost(
      '/players/1/active_playlist',
      {'to_add' : toAdd, 'to_remove' : toRemove}
    )
    self.assertEqual(200, response.status_code, response.content)

    song9 = ActivePlaylistEntry.objects.get(
      song__library__id=1,
      song__lib_id='9',
      state="QE")
    self.assertEqual(1, len(song9.Upvoters))
    self.assertEqual(0, len(song9.Downvoters))
    song10 = ActivePlaylistEntry.objects.get(
      song__library__id='1',
      song__lib_id='10',
      state="QE")
    self.assertEqual(1, len(song10.Upvoters))
    self.assertEqual(0, len(song10.Downvoters))

  @EnsureParticipationUpdated(3,1)
  def testComplexForbiddenRemove(self):
    toAdd = [9,10]
    toRemove = [3]

    response = self.doJSONPost(
      '/players/1/active_playlist',
      {'to_add' : toAdd, 'to_remove' : toRemove}
    )
    self.assertBadPlayerPermission(response)

    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__library__id=1,
      song__lib_id='9',
      state="QE").exists())
    self.assertFalse(ActivePlaylistEntry.objects.filter(
      song__library__id=1,
      song__lib_id='10',
      state="QE").exists())

  @EnsureParticipationUpdated(3,1)
  def testMultiAddWithDuplicateSong(self):
    initialUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).Upvoters)

    toAdd = [{"library_id" : "1", "id" : "1"},{"library_id": "1", "id" : "10" }]
    toRemove = []

    response = self.doJSONPost(
      '/players/1/active_playlist',
      {'to_add' : toAdd, 'to_remove' : toRemove}
    )
    self.assertEqual(200, response.status_code)

    song9 = ActivePlaylistEntry.objects.get(
      song__library__id='1',
      song__lib_id='1',
      state="QE")
    afterUpvoteCount = len(ActivePlaylistEntry.objects.get(song__library__id=1, song__lib_id=1).Upvoters)
    self.assertEqual(initialUpvoteCount+1, afterUpvoteCount)

    song10 = ActivePlaylistEntry.objects.get(
      song__library__id='1',
      song__lib_id='10',
      state="QE")
    self.assertEqual(1, len(song10.Upvoters))
    self.assertEqual(0, len(song10.Downvoters))


class VotingTests(udj.testhelpers.tests07.testclasses.EnsureActiveJeffTest):
  playerid=1

  @EnsureParticipationUpdated(3, 1)
  def testVoteSongUp(self):
    response = self.doPut('/players/1/active_playlist/songs/1/1/upvote')
    self.assertEqual(response.status_code, 200)

    upvote = Vote.objects.get(user__id=3, playlist_entry__song__id=1, weight=1)

  @EnsureParticipationUpdated(3, 1)
  def testVoteDownSong(self):
    response = self.doPut('/players/1/active_playlist/songs/1/1/downvote')
    self.assertEqual(response.status_code, 200)

    upvote = Vote.objects.get(user__id=3, playlist_entry__song__id=1, weight=-1)

  @EnsureParticipationUpdated(3, 1)
  def testBadSongVote(self):
    response = self.doPut('/players/1/active_playlist/songs/1/50/downvote')
    self.assertEqual(response.status_code, 404)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')

  @EnsureParticipationUpdated(3, 1)
  def testDuplicateVote(self):
    response = self.doPut('/players/1/active_playlist/songs/1/2/downvote')
    self.assertEqual(response.status_code, 200)

    upvote = Vote.objects.get(user__id=3, playlist_entry__song__id=2, weight=-1)


  @EnsureParticipationUpdated(3, 1)
  def testUpvoteWithoutPermission(self):
    PlayerPermission(player=Player.objects.get(pk=1),
                     permission="APU",
                     group=PlayerPermissionGroup.objects.get(pk=1)).save()
    response = self.doPut('/players/1/active_playlist/songs/1/1/upvote')
    self.assertBadPlayerPermission(response)

    non_existant_upvote = Vote.objects.filter(user__id=3, playlist_entry__song__id=1, weight=1)
    self.assertFalse(non_existant_upvote.exists())

  @EnsureParticipationUpdated(3, 1)
  def testDownvoteWithoutPermission(self):
    PlayerPermission(player=Player.objects.get(pk=1),
                     permission="APD",
                     group=PlayerPermissionGroup.objects.get(pk=1)).save()
    response = self.doPut('/players/1/active_playlist/songs/1/1/downvote')
    self.assertBadPlayerPermission(response)

    non_existant_upvote = Vote.objects.filter(user__id=3, playlist_entry__song__id=1, weight=-1)
    self.assertFalse(non_existant_upvote.exists())
