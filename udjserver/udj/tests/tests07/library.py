import udj

from udj.testhelpers.tests07.testclasses import KurtisTestCase
from udj.models import Library

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



  def testSimpleLibrariesGet(self):
    response = self.doGet('/libraries')
    self.assertEqual(200, response.status_code, response.content)
    library_json = json.loads(response.content)
    self.assertEqual(9, len(library_json))

    for library in library_json:
      self.verify_library_info(library)



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
