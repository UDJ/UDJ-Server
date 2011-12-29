/**
 * Copyright 2011 Kurtis L. Nusbaum
 * 
 * This file is part of UDJ.
 * 
 * UDJ is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 * 
 * UDJ is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with UDJ.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.klnusbaum.udj;

import android.support.v4.app.ListFragment;
import android.support.v4.app.LoaderManager;
import android.support.v4.content.CursorLoader;
import android.support.v4.content.Loader;
import android.support.v4.widget.CursorAdapter;

import android.os.Bundle;
import android.database.Cursor;
import android.content.Context;
import android.view.View;
import android.widget.TextView;
import android.widget.ImageButton;
import android.view.LayoutInflater;
import android.view.ViewGroup;
import android.util.Log;
import android.content.ContentValues;
import android.accounts.AccountManager;
import android.accounts.Account;

import org.klnusbaum.udj.R;
import org.klnusbaum.udj.containers.Event;

/**
 * Class used for displaying the contents of the Playlist.
 */
public class PlaylistFragment extends ListFragment
  implements LoaderManager.LoaderCallbacks<Cursor>
{

  private static final int PLAYLIST_LOADER_ID = 0;
  private static final int CURRENT_SONG_LOADER_ID = 1;
  private Account account;

  /**
   * Adapter used to help display the contents of the playlist.
   */
  PlaylistAdapter playlistAdapter;

  @Override
  public void onActivityCreated(Bundle savedInstanceState){
    super.onActivityCreated(savedInstanceState);
    account = 
      getActivity().getIntent().getParcelableExtra(Constants.ACCOUNT_EXTRA);
    setEmptyText(getActivity().getString(R.string.no_playlist_items));
    playlistAdapter = new PlaylistAdapter(getActivity(), null);
    LayoutInflater inflater = (LayoutInflater)getActivity().getSystemService(
      Context.LAYOUT_INFLATER_SERVICE);
    View currentSong = inflater.inflate(R.layout.current_song, null);
    getListView().addHeaderView(currentSong);
    setListAdapter(playlistAdapter);
    setListShown(false);
    getLoaderManager().initLoader(PLAYLIST_LOADER_ID, null, this);
  }

  public Loader<Cursor> onCreateLoader(int id, Bundle args){
    switch(id){
    case PLAYLIST_LOADER_ID:
      return new CursorLoader(
        getActivity(), 
        UDJEventProvider.PLAYLIST_URI, 
        null,
        null,
        null,
        UDJEventProvider.PRIORITY_COLUMN);
    default:
      return null;
    }
  }

  public void onLoadFinished(Loader<Cursor> loader, Cursor data){
    playlistAdapter.swapCursor(data);
    if(isResumed()){
      setListShown(true);
    }
    else if(isVisible()){
      setListShownNoAnimation(true);
    }
  }

  public void onLoaderReset(Loader<Cursor> loader){
    playlistAdapter.swapCursor(null);
  }

  private class PlaylistAdapter extends CursorAdapter{
    private long userId;
    private static final String PLAYLIST_ADAPTER_TAG = "PlaylistAdapter";
    public PlaylistAdapter(Context context, Cursor c){
      super(context, c);
      userId = Long.valueOf(AccountManager.get(context).getUserData(
        account, Constants.USER_ID_DATA));
    }

    @Override
    public void bindView(View view, Context context, Cursor cursor){
      int playlistId = cursor.getInt(cursor.getColumnIndex(
        UDJEventProvider.PLAYLIST_ID_COLUMN));

      TextView songName = 
        (TextView)view.findViewById(R.id.playlistSongName);
      songName.setText(cursor.getString(cursor.getColumnIndex(
        UDJEventProvider.TITLE_COLUMN)));

      TextView artist = 
        (TextView)view.findViewById(R.id.playlistArtistName);
      artist.setText(cursor.getString(cursor.getColumnIndex(
        UDJEventProvider.ARTIST_COLUMN)));

      ImageButton upVote = 
        (ImageButton)view.findViewById(R.id.up_vote_button);
      upVote.setTag(String.valueOf(playlistId));
      upVote.setOnClickListener(new View.OnClickListener(){
        public void onClick(View v){
          upVoteClick(v);
        }
      });

      ImageButton downVote = 
        (ImageButton)view.findViewById(R.id.down_vote_button);
      downVote.setTag(String.valueOf(playlistId));
      downVote.setOnClickListener(new View.OnClickListener(){
        public void onClick(View v){
          downVoteClick(v);
        }
      });

      setVoteButtonStates(upVote, downVote, cursor);


      TextView votes = 
        (TextView)view.findViewById(R.id.playlistVotes);
      int totalVotes = 
        cursor.getInt(cursor.getColumnIndex(UDJEventProvider.UP_VOTES_COLUMN))
        -
        cursor.getInt(cursor.getColumnIndex(UDJEventProvider.DOWN_VOTES_COLUMN));
      votes.setText(String.valueOf(totalVotes));
      
    }

    private void setVoteButtonStates(
      ImageButton upVote, ImageButton downVote, Cursor cursor)
    {
      if(
        cursor.getLong(cursor.getColumnIndex(UDJEventProvider.ADDER_ID_COLUMN))
        ==
        userId 
      )
      {
        upVote.setEnabled(false); 
        downVote.setEnabled(false); 
      }
      else if(!cursor.isNull(
        cursor.getColumnIndex(UDJEventProvider.VOTE_TYPE_COLUMN)))
      {
        int voteType = cursor.getInt(
            cursor.getColumnIndex(UDJEventProvider.VOTE_TYPE_COLUMN));
        if(voteType == UDJEventProvider.UP_VOTE_TYPE){
          upVote.setEnabled(false); 
          downVote.setEnabled(true); 
        }
        else{
          upVote.setEnabled(true); 
          downVote.setEnabled(false); 
        }
      }
      else{
        upVote.setEnabled(true); 
        downVote.setEnabled(true); 
      }
    }

    @Override
    public View newView(Context context, Cursor cursor, ViewGroup parent){
      LayoutInflater inflater = (LayoutInflater)context.getSystemService(
        Context.LAYOUT_INFLATER_SERVICE);
      View itemView = inflater.inflate(R.layout.playlist_list_item, null);
      return itemView;
    }
  
    private void upVoteClick(View view){
/*      String playlistId = view.getTag().toString();
      ContentValues toUpdate = new ContentValues();
      toUpdate.put(
        UDJPartyProvider.VOTE_STATUS_COLUMN, UDJPartyProvider.VOTED_UP);
      toUpdate.put(
        UDJPartyProvider.SYNC_STATE_COLUMN, UDJPartyProvider.NEEDS_UP_VOTE);
      getActivity().getContentResolver().update(
        UDJPartyProvider.PLAYLIST_URI,
        toUpdate,
        UDJPartyProvider.PLAYLIST_ID_COLUMN + "= ?",
        new String[]{playlistId});*/
    }
    
    private void downVoteClick(View view){
      /*String playlistId = view.getTag().toString();
      ContentValues toUpdate = new ContentValues();
      toUpdate.put(
        UDJPartyProvider.VOTE_STATUS_COLUMN, UDJPartyProvider.VOTED_DOWN);
      toUpdate.put(
        UDJPartyProvider.SYNC_STATE_COLUMN, UDJPartyProvider.NEEDS_DOWN_VOTE);
      getActivity().getContentResolver().update(
        UDJPartyProvider.PLAYLIST_URI,
      toUpdate,
        UDJPartyProvider.PLAYLIST_ID_COLUMN + "= ?",
      new String[]{playlistId});*/
    }
  }
}

