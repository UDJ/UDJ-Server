from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('udj.views.views07.library',
  url(r'libraries$', 'libraries'),
  url(r'libraries/(?P<library_id>\d+)$', 'library'),
  url(r'libraries/(?P<library_id>\d+)/songs$', 'songs'),
  url(r'libraries/(?P<library_id>\d+)/songs/(?P<song_id>\d+)$', 'delete_song'),
)

urlpatterns += patterns('udj.views.views07.user_modification',
  url(r'user$', 'userMod'),
)

urlpatterns += patterns('udj.views.views07.auth',
  url(r'auth$', 'authenticate'),
  url(r'fb_auth$', 'fb_authenticate'),
)

urlpatterns += patterns('udj.views.views07.server_config',
  url(r'sorting_algorithms$', 'getSortingAlgorithms'),
  url(r'player_search_radius$', 'getAcceptableSearchRadii'),
  url(r'default_player_permissions$', 'getDefaultPlayerPermissions'),
)

urlpatterns += patterns('udj.views.views07.player_search',
  url(r'players$', 'playerSearch'),
)

urlpatterns += patterns('udj.views.views07.player_creation',
  url(r'players/player$', 'createPlayer'),
)

urlpatterns += patterns('udj.views.views07.player_administration',
  url(r'players/(?P<player_id>\d+)/enabled_libraries$', 'getEnabledLibraries'),
  url(r'players/(?P<player_id>\d+)/enabled_libraries/(?P<library_id>\d+)$', 'modEnabledLibraries'),
  url(r'players/(?P<player_id>\d+)/password$', 'modifyPlayerPassword'),
  url(r'players/(?P<player_id>\d+)/location$', 'modLocation'),
  url(r'players/(?P<player_id>\d+)/sorting_algorithm$', 'setSortingAlgorithm'),
  url(r'players/(?P<player_id>\d+)/state$', 'setPlayerState'),
  url(r'players/(?P<player_id>\d+)/volume$', 'setPlayerVolume'),
  url(r'players/(?P<player_id>\d+)/kicked_users/(?P<kick_user_id>\d+)$', 'kickUser'),
  url(r'players/(?P<player_id>\d+)/banned_users/(?P<ban_user_id>\d+)$', 'modBans'),
  url(r'players/(?P<player_id>\d+)/banned_users$', 'getBannedUsers'),
  url(r'players/(?P<player_id>\d+)/permissions$', 'getPlayerPermissions'),
  url(r'players/(?P<player_id>\d+)/permissions/(?P<permission_name>\S+)/groups/(?P<group_name>.+)$',
    'modPlayerPermissions'),
  url(r'players/(?P<player_id>\d+)/permission_groups$', 'getPermissionGroups'),


  url(r'players/(?P<player_id>\d+)/permission_groups/(?P<group_name>.+)/members$',
    'getPermissionGroupMembers'),
  url(r'players/(?P<player_id>\d+)/permission_groups/(?P<group_name>.+)/members/(?P<user_id>\d+)$',
    'modPermissionGroupMembers'),

  url(r'players/(?P<player_id>\d+)/permission_groups/(?P<group_name>.+)$', 'modPlayerPermissionGroup'),
)

urlpatterns += patterns('udj.views.views07.player_interaction',
  url(r'players/(?P<player_id>\d+)/users/user$', 'modPlayerParticiapants'),
  url(r'players/(?P<player_id>\d+)/users$', 'getUsersForPlayer'),
  url(r'players/(?P<player_id>\d+)/available_music$', 'getAvailableMusic'),
  url(r'players/(?P<player_id>\d+)/available_music/artists$', 'getArtists'),
  url(r'players/(?P<player_id>\d+)/available_music/artists/(?P<givenArtist>.*)$', 'getArtistSongs'),
  url(r'players/(?P<player_id>\d+)/recently_played$', 'getRecentlyPlayed'),
  url(r'players/(?P<player_id>\d+)/available_music/random_songs$', 'getRandomSongsForPlayer'),
  url(r'players/(?P<player_id>\d+)/current_song$', 'modCurrentSong'),
)

urlpatterns += patterns('udj.views.views07.active_playlist',
  url(r'players/(?P<player_id>\d+)/active_playlist$', 'activePlaylist'),
  url(r'players/(?P<player_id>\d+)/active_playlist/songs/(?P<library_id>\d+)/(?P<lib_id>\d+)/upvote$',
    'voteSongUp'),
  url(r'players/(?P<player_id>\d+)/active_playlist/songs/(?P<library_id>\d+)/(?P<lib_id>\d+)/downvote$',
    'voteSongDown'),
  url(r'players/(?P<player_id>\d+)/active_playlist/songs/(?P<library_id>\d+)/(?P<song_id>.*)$', 'modActivePlaylist'),
)




"""
urlpatterns += patterns('udj.views.views07.favorites',
  (r'favorites/players/(?P<player_id>\d+)/(?P<lib_id>\d+)$', 'favorite'),
  (r'favorites/players/(?P<player_id>\d+)$', 'getFavorites'),
)

"""

"""
urlpatterns += patterns('udj.views.views07.ban_music',
  (r'players/(?P<player_id>\d+)/ban_music/(?P<lib_id>\d+)$', 'modifyBanList'),
  (r'players/(?P<player_id>\d+)/ban_music$', 'multiBan'),
)

"""
