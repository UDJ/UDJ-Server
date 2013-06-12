import udj

from udj.testhelpers.tests07.testclasses import KurtisTestCase
from udj.models import Library, AssociatedLibrary, LibraryEntry
from udj.headers import FORBIDDEN_REASON_HEADER

import json

class LibTestCases(KurtisTestCase):

  def verifySongAdded(self, library_id, jsonSong):
    addedSong = LibraryEntry.objects.get(library__id=library_id, lib_id=jsonSong['id'])
    self.assertEqual(addedSong.title, jsonSong['title'])
    self.assertEqual(addedSong.artist, jsonSong['artist'])
    self.assertEqual(addedSong.album, jsonSong['album'])
    self.assertEqual(addedSong.track, jsonSong['track'])
    self.assertEqual(addedSong.genre, jsonSong['genre'])
    self.assertEqual(addedSong.duration, jsonSong['duration'])

  def verify_library_info(self, library):
    actual_library = Library.objects.get(id=int(library['id']))
    self.assertEqual(actual_library.name, library['name'])
    self.assertEqual(actual_library.description, library['description'])
    self.assertEqual(actual_library.pub_key, library['pub_key'])
    self.assertEqual(actual_library.get_read_permission_display(), library['read_permission'])
    self.assertEqual(actual_library.get_write_permission_display(), library['write_permission'])
    if actual_library.Owner:
      self.assertEqual(actual_library.Owner.id, int(library['owner']['id']))
    else:
      self.assertEqual({}, library['owner'])
    self.assertEqual(actual_library.IsOfficial, library['is_official'])

  def verify_correct_library_ids(self, library_json, required_ids):
    self.assertEqual(len(required_ids), len(library_json))
    for library in library_json:
      self.assertTrue(library['id'] in required_ids,
                      "{0} is not in {1}".format(library['id'], required_ids))


  def testSimpleLibrariesGet(self):
    response = self.doGet('/libraries')
    self.assertGoodJSONResponse(response)
    library_json = json.loads(response.content)
    self.assertEqual(9, len(library_json))

    for library in library_json:
      self.verify_library_info(library)


  def testSearchLibraryByOwner(self):
    response = self.doGet('/libraries?owner=2')
    self.assertGoodJSONResponse(response)
    self.verify_correct_library_ids(json.loads(response.content),
                                    [u'1', u'2', u'4', u'5', u'6', u'7'])

  def testSearchForOfficialLibraries(self):
    response = self.doGet('/libraries?is_official=true')
    self.assertGoodJSONResponse(response)
    self.verify_correct_library_ids(json.loads(response.content), [u'8'])

  def testSearchForLibrariesByName(self):
    response = self.doGet('/libraries?name=default')
    self.assertGoodJSONResponse(response)
    self.verify_correct_library_ids(json.loads(response.content),
                                    [u'1', u'3', u'2', u'4', u'5', u'6', u'7'])


  def testSearchLibrariesByReadable(self):
    response = self.doGet('/libraries?is_readable=true')
    self.assertGoodJSONResponse(response)
    self.verify_correct_library_ids(json.loads(response.content),
                                    [u'1', u'2', u'4', u'5', u'6', u'7', u'8'])

  def testLimitedSearch(self):
    response = self.doGet('/libraries?max_results=3&start_position=2')
    self.assertGoodJSONResponse(response)
    self.verify_correct_library_ids(json.loads(response.content),
                                    [u'3', u'4', u'5'])

  def testCreateLibrary(self):
    payload = {
               "name" : "creation test library",
               "description" : "a library to test library creation",
               "public_key" : "alldkjek"
              }
    response = self.doJSONPut("/libraries", payload)
    self.assertGoodJSONResponse(response, 201)
    returned_json = json.loads(response.content)
    new_library = Library.objects.get(pk=int(returned_json['id']))
    self.assertEqual(new_library.name, payload['name'])
    self.assertEqual(new_library.description, payload['description'])
    self.assertEqual(new_library.pub_key, payload['public_key'])
    self.assertEqual(new_library.get_read_permission_display(), 'owner')
    self.assertEqual(new_library.get_write_permission_display(), 'owner')
    self.assertEqual(new_library.Owner.id, 2)
    self.assertEqual(new_library.IsOfficial, False)

  def testBadCreateLibrary(self):
    orig_num_libraries = len(Library.objects.all())
    payload = {
               "name" : "creation test library",
               "description" : "a library to test library creation",
              }
    response = self.doJSONPut("/libraries", payload)
    self.assertEqual(400, response.status_code)
    self.assertEqual(orig_num_libraries, len(Library.objects.all()))


  def testGetSpecificLibrary(self):
    response = self.doGet('/libraries/1')
    self.assertGoodJSONResponse(response)
    library_json = json.loads(response.content)
    self.assertEqual(u'1', library_json['id'])
    self.assertEqual(u'Kurtis Player Default Library', library_json['name'])
    self.assertEqual(u'blah', library_json['description'])
    self.assertEqual(u'blkjdd', library_json['pub_key'])
    self.assertEqual(u'owner', library_json['read_permission'])
    self.assertEqual(u'owner', library_json['write_permission'])
    self.assertEqual(u'2', library_json['owner']['id'])
    self.assertEqual(False, library_json['is_official'])

  def testBadGetSpecificLibrary(self):
    response = self.doGet('/libraries/99999')
    self.assertMissingResponse(response, 'library')

  def testDeleteLibrary(self):
    response = self.doDelete('/libraries/1')
    self.assertEqual(200, response.status_code)

    deleted_library = Library.objects.get(pk=1)

    self.assertTrue(deleted_library.is_deleted)

    for entry in LibraryEntry.objects.filter(library=deleted_library):
      self.assertTrue(entry.is_deleted)

    for assoc_lib in AssociatedLibrary.objects.filter(library=deleted_library):
      self.assertFalse(assoc_lib.enabled)

  def testNoWritePermissionLibraryDelete(self):
    response = self.doDelete('/libraries/3')
    self.assertEqual(403, response.status_code)
    self.assertEqual('write-permission', response[FORBIDDEN_REASON_HEADER])

    non_deleted_library = Library.objects.get(pk=3)

    self.assertFalse(non_deleted_library.is_deleted)

  def testDeleteNonExistentLibrary(self):
    response = self.doDelete('/libraries/999999')
    self.assertMissingResponse(response, 'library')


  def testModLibraryName(self):
    payload = {'name' : 'This is the new name! (just like the old name)'}
    response = self.doJSONPost('/libraries/1', payload)
    self.assertEqual(200, response.status_code)
    changed_library = Library.objects.get(pk=1)
    self.assertTrue(changed_library.name, payload['name'])

  def testModLibraryDescription(self):
    payload = {'description' : 'This is the new name! (just like the old name)'}
    response = self.doJSONPost('/libraries/1', payload)
    self.assertEqual(200, response.status_code)
    changed_library = Library.objects.get(pk=1)
    self.assertTrue(changed_library.description, payload['description'])

  def testModLibraryPubKey(self):
    payload = {'pub_key' : 'newpubkey'}
    response = self.doJSONPost('/libraries/1', payload)
    self.assertEqual(200, response.status_code)
    changed_library = Library.objects.get(pk=1)
    self.assertTrue(changed_library.pub_key, payload['pub_key'])

  def testBadLibraryInfoMod(self):
    payload = {'pub_key' : 'newpubkey'}
    response = self.doJSONPost('/libraries/3', payload)
    self.assertBadPermission(response, 'write-permission')

  def testNonExistentLibraryInfoMod(self):
    payload = {'pub_key' : 'newpubkey'}
    response = self.doJSONPost('/libraries/99999999', payload)
    self.assertMissingResponse(response, 'library')

  """
  def testSimpleAdd(self):
    payload = {
      "id" : "11",
      "title" : "Zero",
      "artist" : "The Smashing Pumpkins",
      "album" : "Mellon Collie And The Infinite Sadness",
      "track" : 4,
      "genre" : "Rock",
      "duration" : 160
    }

    response = self.doJSONPut('/libraries/1/songs', payload)
    self.assertEqual(201, response.status_code, response.content)
    self.verifySongAdded(1, payload)

  def testDuplicateAdd(self):
    payload = [{
      "id" : "10",
      "title" : "My Name Is Skrillex",
      "artist" : "Skrillex",
      "album" : "My Name Is Skrillex",
      "track" : 1,
      "genre" : "Dubstep",
      "duration" : 291
    }]

    response = self.doJSONPut('/udj/0_6/players/1/library/songs', json.dumps(payload))
    self.assertEqual(201, response.status_code, response.content)

  def testBadDuplicateAdd(self):
    payload = [{
      "id" : "10",
      "title" : "Name Is Skrillex",
      "artist" : "Skrillex",
      "album" : "My Name Is Skirllex",
      "track" : 1,
      "genre" : "Dubstep",
      "duration" : 291
    }]

    response = self.doJSONPut('/udj/0_6/players/1/library/songs', json.dumps(payload))
    self.assertEqual(409, response.status_code, response.content)


  def testDelete(self):
    response = self.doDelete('/udj/0_6/players/1/library/10')
    self.assertEqual(200, response.status_code, response.content)
    self.assertEqual(True, LibraryEntry.objects.get(library__id=1, lib_id=10).is_deleted)

  def testDeleteOnPlaylist(self):
    response = self.doDelete('/udj/0_6/players/1/library/5')
    self.assertEqual(200, response.status_code, response.content)
    self.assertEqual(True, LibraryEntry.objects.get(library__id=1, lib_id=5).is_deleted)
    self.assertEqual(u'RM', ActivePlaylistEntry.objects.get(pk=4).state)

  def testBadDelete(self):
    response = self.doDelete('/udj/0_6/players/1/library/12')
    self.assertEqual(404, response.status_code, response.content)
    self.assertEqual(response[MISSING_RESOURCE_HEADER], 'song')


  def testMultiMod(self):
    to_add = [{
      "id" : "11",
      "title" : "Zero",
      "artist" : "The Smashing Pumpkins",
      "album" : "Mellon Collie And The Infinite Sadness",
      "track" : 4,
      "genre" : "Rock",
      "duration" : 160
    }]

    to_delete = [1,2]

    response = self.doPost('/udj/0_6/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(200, response.status_code, response.content)
    self.verifySongAdded(to_add[0])
    self.assertEqual(True, LibraryEntry.objects.get(library__id=1, lib_id=1).is_deleted)
    self.assertEqual(True, LibraryEntry.objects.get(library__id=1, lib_id=2).is_deleted)

  def testDuplicateMultiModAdd(self):
    to_add = [{
      "id": "2",
      "title": "Narcolepsy",
      "artist": "Third Eye Blind",
      "album": "Third Eye Blind",
      "track": 2,
      "genre": "Rock",
      "duration": 228,
    },
    {
      "id": "11",
      "title": "Fuel",
      "artist": "Metallica",
      "album": "Reload",
      "track": 2,
      "genre": "Rock",
      "duration": 266,
    } 
    ]
    to_delete=[]
    response = self.doPost('/udj/0_6/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(200, response.status_code, response.content)
    #Make sure fuel got inserted.
    fuel = LibraryEntry.objects.get(library__id=1, lib_id='11')


  def testBadDuplicateMultiModAdd(self):
    to_add = [{
      "id": "1",
      "title": "Semi-Charmed Life",
      "artist": "Third Eye Blind",
      "album": "blah",
      "track": 3,
      "genre": "Rock",
      "duration": 268
    },
    {
      "id": "2",
      "title": "Narcolepsy",
      "artist": "Third Eye Blind",
      "album": "Third Eye Blind",
      "track": 2,
      "genre": "Rock",
      "duration": 228,
    },
    {
      "id": "11",
      "title": "Fuel",
      "artist": "Metallica",
      "album": "Reload",
      "track": 2,
      "genre": "Rock",
      "duration": 266,
    } 
    ]
    to_delete=[]
    response = self.doPost('/udj/0_6/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(409, response.status_code, response.content)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    self.assertEqual(['1'], jsonResponse)
    #Make sure we didn't add fuel because this was a bad one
    self.assertFalse(LibraryEntry.objects.filter(library__id=1, lib_id=11).exists())


  def testBadMultiModRemove(self):
    to_add = [{
      "id": "11",
      "title": "Fuel",
      "artist": "Metallica",
      "album": "Reload",
      "track": 2,
      "genre": "Rock",
      "duration": 266,
    }
    ]
    to_delete=['1','14']
    response = self.doPost('/udj/0_6/players/1/library',
      {'to_add' : json.dumps(to_add), 'to_delete' : json.dumps(to_delete)})

    self.assertEqual(404, response.status_code, response.content)
    self.isJSONResponse(response)
    jsonResponse = json.loads(response.content)
    self.assertEqual(['14'], jsonResponse, jsonResponse)
    #Make sure we didn't add Fuel because this was a bad one
    self.assertFalse(LibraryEntry.objects.filter(library__id=1, lib_id=11).exists())
    #Make sure we didn't delete Semi-Charmed Life because this request was bad
    self.assertTrue(LibraryEntry.objects.filter(library__id=1, lib_id=1, is_deleted=False).exists())

"""
