""" Tracks your friends's music streaming activity on Spotify and adds the tracks to a playlist.
"""

import sqlite3
import json
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import pandas as pd
import datetime
import subprocess
import csv
import time
import clint_id_secret
from dateutil import parser
import sys
from threading import Thread, Timer
import time


# # local imports
# import json_to_sqlite

# set the client_ID, client_SECRET, redirect_uri and username for the spotify api authentication

redirect_uri = 'http://127.0.0.1:9090'
username = 'rt47etgc6xpwhhhb8575rth83'
client_ID = clint_id_secret.client_ID
client_SECRET = clint_id_secret.client_SECRET

# data_folder = r"C:\Users\saket\Documents\1.MY_DATA\spotify\spotify api data"
recently_played_file_name = 'recently_played_tracks.csv'

client_credentials_manager = spotipy.oauth2.SpotifyOAuth(
        # scope=scope,
        username=username,
        client_id=client_ID,
        client_secret=client_SECRET,
        redirect_uri=redirect_uri,
        # open_browser=False
        )

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10, retries=10)
    

# returns a spotipy object with the given scope
def get_spotify_token(scope):
    client_credentials_manager.get_access_token(as_dict=False)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10, retries=10)


""" ATTENTION you can find a better way, so that you don't have to get the every token everytime"""
# token to modify user's playlists
playlist_modify_public = get_spotify_token("playlist-modify-public")

# user-read-recently-played
user_read_recently_played = get_spotify_token("user-read-recently-played")

# user-top-read
user_top_read = get_spotify_token("user-top-read")

# playlist-modify-private
playlist_modify_private = get_spotify_token("playlist-modify-private")

# user-library-read
user_library_read = get_spotify_token("user-library-read")

# playlist-read-private
playlist_read_private = get_spotify_token("playlist-read-private")

# get all the tracks from a private playlist
def get_playlist_tracks(playlist_id):
    """Get all the playlists that are new from the user's playlists info.

    Parameters
    ----------
    None

    Returns
    -------
    new_playlists : pd.DataFrame
        A data frame with the new playlists info and date.
    """

    results = playlist_read_private.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

""" ATTENTION needed here Need to be updated """
# retry 3 times to get the playlist tracks
def get_playlist_tracks_retry(playlist_id):
    """retry 3 times to get the playlist tracks

    Parameters
    ----------
    playlist_id : str

    Returns
    -------
    results : dict
    """
    for i in range(9999**9999):
        try:
            results = get_playlist_tracks(playlist_id)
            return results
        except Exception as e:
            print(f"Error fetching playlist tracks: {e}")
            print(f"Retrying in 10 seconds ({i+1}/20 attempts)...")
            if i < 3:
                time.sleep(10)
                print('sleeping for 10 seconds')
            elif i < 5:
                time.sleep(30)
                print('sleeping for 30 seconds')
            else:
                time.sleep(60)
                print('sleeping for 60 seconds')
    return None


def get_recently_played_tracks(limit=50):
    """ Get the recently played tracks from the user's account.

    parameters
    ----------
    limit : int (default=50)
        The number of tracks to return. Default: 50. Minimum: 1. Maximum: 50.
    
    Returns
    -------
    recently_played : dict
    """
    recently_played = user_read_recently_played.current_user_recently_played(limit=limit, )
    return recently_played

def add_to_playlist(playlist_id, list_of_tracks):
    """ Add the tracks to the playlist.

    Parameters
    ----------
    playlist_id : str
        The playlist id.

    list_of_tracks : list
        The list of tracks to add to the playlist.
    """
    splity_split = split_with_no(list_of_tracks, 100)
    for hundred_lis in splity_split:
        playlist_modify_private.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=hundred_lis)


def split_with_no(list, No):
    """splits the list into sublists of size 100

    Parameters
    ----------
    list : list
        The list to split.
    No : int
        The size of the sublists.

    Returns
    -------
    lists : list
    """
    if type(list) == str:
        return [list]
    lists = []
    no = 0
    listy = []
    for i in list:
        if no < 100:
            no += 1
            listy.append(i)
        else:
            lists.append(listy) 
            listy = []
            no = 0
    lists.append(listy)
    print('len - ',len(lists))
    return lists

# returns the top 50 tracks played by the user
def get_top_tracks(limit=50):
    """ Get the top tracks from the user's account.

    Parameters
    ----------
    limit : int (default=50)
        The number of tracks to return. Default: 50. Minimum: 1. Maximum: 50.

    Returns
    -------
    top_tracks : dict
    """
    top_tracks = token.current_user_top_tracks(limit=limit)
    return top_tracks

""" ATTENTION needed here Need to be updated """
# returns a datetime object from the given timestamp
def timestamp_to_time(timestamp):
    """returns a datetime object from the given timestamp

    Parameters
    ----------
    timestamp : str

    Returns
    -------
    dt_object : datetime.datetime
    """
    try:
        # Try to parse the timestamp string as ISO format with microsecond component
        dt_object = datetime.datetime.fromisoformat(timestamp[:-1])
    except ValueError:
        try:
            # Try to parse the timestamp string as ISO format without microsecond component
            dt_object = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # Try to parse the timestamp string as a Unix timestamp in seconds
            dt_object = datetime.datetime.fromtimestamp(int(timestamp))

    return dt_object

# returns a dictionary with the track info for the given track
def get_track_info_from_json(track_dict):
    """returns a dictionary with the track info for the given track

    Parameters
    ----------
    track_dict : dict

    Returns
    -------
    track_info : dict
    """
    # iterate through all the keys in the track_json try to get the value of the key, else set the value to None
    track_info = {}
    for key in track_dict.keys():
        try:
            track_info[key] = track_json[key]
        except:
            track_info[key] = None
    return track_info

def parse_streaming_history():

  # Call the get_recently_played_tracks function and store the result in a variable.
  data = get_recently_played_tracks()

  # Create an empty list to store the parsed data.
  parsed_data = []

  # Loop through the items in the data list.
  for item in data["items"]:

    # Get the track object.
    track = item["track"]

    # Get the artist/artists data.
    artists = track["artists"]
    artist_names = []
    artist_ids = []
    for artist in artists:
      artist_names.append(artist["name"])
      artist_ids.append(artist["id"])

    # Get the album data.
    album = track["album"]
    album_name = album["name"]
    album_id = album["id"]
    album_type = album["album_type"]
    release_date = album["release_date"]
    total_tracks = album["total_tracks"]

    # Get the image with 300 height from the images list.
    images = album["images"]
    image_300 = None
    for image in images:
      if image["height"] == 300:
        image_300 = image["url"]
        break

    # Get the track data.
    track_name = track["name"]
    track_number = track["track_number"]
    duration_ms = track["duration_ms"]
    disc_number = track["disc_number"]
    popularity = track["popularity"]
    preview_url = track["preview_url"]

    # Get the played_at data.
    played_at = item["played_at"]

    # Get the track id from the uri by removing the spotify:track: prefix.
    track_id = track["uri"].replace("spotify:track:", "")

    # Get the context data.
    
    try:
      context = item["context"]
      context_type = context["type"]
      context_uri = context["uri"]
    except:
      context_uri = None
      context_type = None

    # Create a dictionary to store the parsed data for each item.
    item_data = {
      # Artist details
      "artist_names": artist_names,
      "artist_uris": artist_ids,
      # Album details
      "album_name": album_name,
      "album_uri": album_id,
      "album_type": album_type,
      "release_date": release_date,
      "total_tracks": total_tracks,
      "image_url": image_300,
      # Track details
      "track_name": track_name,
      "track_number": track_number,
      "duration_ms": duration_ms,
      "disc_number": disc_number,
      "popularity": popularity,
      "preview_url": preview_url,
      "played_at": played_at,
      "track_uri": track_id,
      # Context details
      "context_type": context_type,
      "context_uri": context_uri
    }

    # Append the item data to the parsed data list.
    parsed_data.append(item_data)

  # Return the parsed data list.
  return parsed_data



# """ ATTENTION needed here Need to be updated """
# # stores the recently played tracks in a csv file
# def store_recently_played_tracks():
#     """stores the recently played tracks in a csv file
#     """
#     # get the recently played tracks
#     recently_played_tracks = get_recently_played_tracks_info()
#     # create a dataframe from the stored recently played tracks
#     old_recently_played_tracks = pd.read_csv(recently_played_file_name)
#     # create a dataframe from the list of recently played tracks
#     new_recently_played_tracks = pd.DataFrame(recently_played_tracks)
#     # get the last played track from the old_recently_played_tracks
#     last_played_at = old_recently_played_tracks['played_at'].iloc[-1]
#     # reverse the new_recently_played_tracks
#     new_recently_played_tracks = new_recently_played_tracks.iloc[::-1]

#     # iterate though all the new_recently_played_tracks and find the one which is closest to the last_played_at
#     for i in range(len(new_recently_played_tracks)):
#         # get the difference between the last_played_at and the current track's played_at in hours
#         diff = (timestamp_to_time(last_played_at) - timestamp_to_time(new_recently_played_tracks['played_at'].iloc[i])).total_seconds() / 3600
#         # if the difference is negative, then the current track is the one which was last played
#         if diff < 0:
#             # get the index of the new_recently_played_tracks
#             index = i
#             # start the new_recently_played_tracks from the index
#             new_recently_played_tracks = new_recently_played_tracks.iloc[index:]
#             # iterate through all the new_recently_played_tracks and print the track name and time
#             print("Newly added tracks:")
#             for j in range(len(new_recently_played_tracks)):
#                 print(new_recently_played_tracks['played_at'].iloc[j], new_recently_played_tracks['track_name'].iloc[j])
#             # add the new_recently_played_tracks to the old_recently_played_tracks, use .concat() to avoid the index being repeated
#             old_recently_played_tracks = pd.concat([old_recently_played_tracks, new_recently_played_tracks])
#             # save the old_recently_played_tracks to the csv file
#             old_recently_played_tracks.to_csv(recently_played_file_name, index=False)
#             break
# modify this function so that it could store the data to a sqllite database instead of csv
def get_top_tracks(limit=200):
    """returns the top tracks

    Parameters
    ----------
    limit : int, optional
        The number of entities to return. Default is 200. Minimum is 1. Maximum is 200(I guess # need to make sure)
    
    Returns
    -------
    top_tracks : dict
    """
    top_tracks = user_top_read.current_user_top_tracks(limit=limit, time_range='short_term')
    return top_tracks

# returns the top tracks info in a list
def get_top_tracks_info():
    top_tracks = get_top_tracks()
    top_tracks_info = []
    for i in range(len(top_tracks['items'])):
        track = top_tracks['items'][i]
        track_info = {
            'track_name': track['name'],
            'track_id': track['id'],
            'track_duration': track['duration_ms'],
            'track_popularity': track['popularity'],
            'track_explicit': track['explicit'],
            'album_name': track['album']['name'],
            'album_id': track['album']['id'],
            'album_release_date': track['album']['release_date'],
            'album_release_date_precision': track['album']['release_date_precision'],
            'album_total_tracks': track['album']['total_tracks'],
            'album_type': track['album']['album_type'],
            'artist_name': track['artists'][0]['name'],
            'artist_id': track['artists'][0]['id']
        }
        top_tracks_info.append(track_info)
    return top_tracks_info

def get_top_artists_info(limit=200):
    """returns the top artists info in a list

    Parameters
    ----------
    limit : int, optional
        The number of entities to return.

    Returns
    -------
    top_artists_info : list
    """
    top_artists = user_top_read.current_user_top_artists(limit=limit)
    top_artists_info = []
    for i in range(len(top_artists['items'])):
        artist = top_artists['items'][i]
        artist_info = {
            'artist_name': artist['name'],
            'artist_id': artist['id'],
            'artist_popularity': artist['popularity'],
            'artist_followers': artist['followers']['total'],
            'artist_genres': artist['genres']
        }
        top_artists_info.append(artist_info)
    return top_artists_info

# returns the user's top genres in a list
def get_top_genres_info(limit=200):
    """returns the user's top genres in a list

    Parameters
    ----------
    limit : int, optional
        The number of entities to return.

    Returns
    -------
    top_genres_info : list
    """
    top_artists = user_top_read.current_user_top_artists(limit=limit)
    top_genres_info = []
    for i in range(len(top_artists['items'])):
        artist = top_artists['items'][i]
        for j in range(len(artist['genres'])):
            genre = artist['genres'][j]
            genre_info = {
                'genre': genre
            }
            top_genres_info.append(genre_info)
    return top_genres_info

# returns the user's library tracks in a list
def get_library_info(limit=200):
    """returns the user's library tracks in a list

    Parameters
    ----------
    limit : int, optional
        The number of entities to return.

    Returns
    -------
    library_info : list
    """
    # get the token for the user-library-read scope
    # get the user's library data
    library = user_library_read.current_user_saved_tracks(limit=limit)

    # convert the library data to a dataframe
    library_df = pd.DataFrame(library)
    return library_df

# returns a list of dictionaries containing the user's playlists
def get_user_playlists():
    """ returns a list of dictionaries containing the user's playlists

    Returns
    -------
    user_playlists : list
        list of dictionaries containing the user's playlists
    """
    user_playlists = playlist_read_private.current_user_playlists(limit=50)
    return user_playlists

# # returns a list of dictionaries containing the user's playlists
# def store_user_playlists_info():
#     user_playlists_info = get_user_playlists_info()
#     user_playlists_info_df = pd.DataFrame(user_playlists_info)
#     user_playlists_info_df.to_csv('user_playlists_info.csv', index=False)

# returns the tracks in a playlist in a dictionary
def get_user_playlist_tracks(playlist_id):
    """ returns the tracks in a playlist in a dictionary

    Parameters
    ----------
    playlist_id : str
        The Spotify ID for the playlist.

    Returns
    -------
    user_playlist_tracks : dict
        The tracks in a playlist in a dictionary
    """
    user_playlist_tracks = playlist_read_private.user_playlist_tracks(playlist_id)
    return user_playlist_tracks

""" ATTENTION: This function is not working properly."""
def sort_playlist_by_popularity():
    """ Sorts the playlist by popularity

    Returns
    -------
    sorted_playlist : list
        The tracks in a playlist sorted by popularity
    """
    user_playlist_tracks = get_user_playlist_tracks(playlist_id)

# returns the tracks in a playlist in a list of dictionaries
def get_user_playlist_tracks_info(playlist_id):
    """ returns the tracks in a playlist in a list of dictionaries

    Parameters
    ----------
    playlist_id : str
        The Spotify ID for the playlist.

    Returns
    -------
    user_playlist_tracks_info : list
        The tracks in a playlist in a list of dictionaries
    """
    user_playlist_tracks = get_user_playlist_tracks(playlist_id)
    user_playlist_tracks_info = []
    for i in range(len(user_playlist_tracks['items'])):
        track = user_playlist_tracks['items'][i]['track']
        return track
        track_info = {
            'track_name': track['name'],
            'track_id': track['id'],
            'track_duration': track['duration_ms'],
            'track_popularity': track['popularity'],
            'track_explicit': track['explicit'],
            'album_name': track['album']['name'],
            'album_id': track['album']['id'],
            'album_release_date': track['album']['release_date'],
            'album_release_date_precision': track['album']['release_date_precision'],
            'album_total_tracks': track['album']['total_tracks'],
            'album_type': track['album']['album_type'],
            'artist_name': track['artists'][0]['name'],
            'artist_id': track['artists'][0]['id']
        }
        user_playlist_tracks_info.append(track_info)
    return user_playlist_tracks_info

# returns a json of recommended tracks according to the seed artists, genres and tracks
def get_recommendations(seed_artists, seed_genres, seed_tracks):
    """ returns a json of recommended tracks according to the seed artists, genres and tracks

    Parameters
    ----------
    seed_artists : list
        A list of Spotify ID/IDs for seed artists.
    seed_genres : list
        A list of any genres in the set of available genre seeds.
    seed_tracks : list
        A list of Spotify ID/IDs for seed tracks.

    Returns
    -------
    recommendations : dict
        A json of recommended tracks according to the seed artists, genres and tracks
    """
    recommendations = user_top_read.recommendations(seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks)
    return recommendations

def get_recommendations_info(seed_artists, seed_genres, seed_tracks):
    """ returns a list of dictionaries containing the important info from recommendations json

    Parameters
    ----------
    seed_artists : list
        A list of Spotify ID/IDs for seed artists.
    seed_genres : list
        A list of any genres in the set of available genre seeds.
    seed_tracks : list
        A list of Spotify ID/IDs for seed tracks.

    Returns
    -------
    recommendations_info : list
        A list of dictionaries containing the important info from recommendations json
    """
    # get the json of the recommended tracks
    recommendations = get_recommendations(seed_artists, seed_genres, seed_tracks)
    recommendations_info = []
    # get the info of each track
    for i in range(len(recommendations['tracks'])):
        track = recommendations['tracks'][i]
        track_info = get_track_info_from_json(track)
        recommendations_info.append(track_info)
    return recommendations_info

# returns the user's saved albums in a list
def get_saved_albums():
    """
    Returns
    -------
    saved_albums : list
        The user's saved albums in a list
    """
    saved_albums = user_library_read.current_user_saved_albums()
    return saved_albums

# returns the user's saved shows in a list
def get_saved_shows():
    """
    Returns
    -------
    saved_shows : list
        The user's saved shows in a list
    """
    saved_shows = user_library_read.current_user_saved_shows()
    return saved_shows

# returns the user's saved episodes in a list
def get_saved_episodes():
    """
    Returns
    -------
    saved_episodes : list
        The user's saved episodes in a list
    """
    saved_episodes = user_library_read.current_user_saved_episodes()
    return saved_episodes

def get_library_info(limit):
    """
    Parameters
    ----------
    limit : int
        The number of tracks to return. Default: 20. Minimum: 1. Maximum: 50.
    
    Returns
    -------
    library_df : pandas dataframe
        The user's library data in a pandas dataframe
    """
    # get the user's library data
    library = user_library_read.current_user_saved_tracks(limit=limit)
    # convert the library data to a dataframe
    library_df = pd.DataFrame(library)
    return library_df

# Define a function to get the value of a nested key from a dictionary
def get_nested_value(dictionary, keys, default=''):
    """ Returns the value of a nested key from a dictionary

    Parameters
    ----------
    dictionary : dict
        The dictionary to get the value from
    keys : list
        A list of keys to get the value from
    default : str
        The default value to return if the key is not found

    Returns
    -------
    dictionary : dict
        The dictionary to get the value from
    keys : list
        A list of keys to get the value from
    default : str
        The default value to return if the key is not found
    """
    # Loop through the keys
    for key in keys:
        # Try to get the value of the current key
        try :
            dictionary = dictionary[key]
        # If the key is not found, return the default value
        except :
            return default
    # Return the final value
    return dictionary

# returns a list of dictionaries containing the user's playlists information
def get_user_playlists_info():
    """ Returns a list of dictionaries containing the user's playlists information
    Parameters:
    ----------
    None

    Returns:
    -------
    user_playlists_info: list of dictionaries
    """
    user_playlists = get_user_playlists()
    user_playlists_info = []
    for i in range(len(user_playlists['items'])):
        playlist = user_playlists['items'][i]
        playlist_info = {
            'playlist_name': playlist['name'],
            'playlist_id': playlist['id'],
            'playlist_description': playlist['description'],
            'playlist_tracks': playlist['tracks']['total'],
            'playlist_owner': playlist['owner']['display_name'],
            'playlist_owner_id': playlist['owner']['id'],
            'playlist_public': playlist['public'],
            'playlist_collaborative': playlist['collaborative'],
        }
        if playlist.get('images'):
            playlist_info['playlist_images'] = playlist['images'][0].get('url', '')
        else:
            playlist_info['playlist_images'] = ''
        # playlist_info['playlist_images'] = playlist.get('images', [{}])[0].get('url', '')

        user_playlists_info.append(playlist_info)
    return user_playlists_info


# """ ATTENTION NEEDED HERE"""
# # store the user's playlists information in a csv file
# def store_user_playlists_info():
#     """change to to store into to a sql database
#     """
#     user_playlists_info = get_user_playlists_info()
#     df = pd.DataFrame(user_playlists_info)
#     # add a column with the current date and time
#     df['date'] = datetime.datetime.now()
#     df.to_csv('user_playlists_info.csv', index=False)

# get the commands stored in the playlist name or description
def gather_functions(string):
    """ uses regex to get the commands stored in the playlist name or description

    Parameters
    ----------
    string : str
        The string to get the functions from

    Returns
    -------
    functions : list
        A list of functions that contains a list of words(commands) to be performed on the playlist
    """
    # lowercases the string
    test = string.lower()
    # write a regex to get the artist which should return swans
    artist = re.search(r'artist-(\w+(?:-\w+)*)', string)
    # write a regex to get the gather which should return gather-all
    gather = re.search(r'gather-(\w+(?:-\w+)*)', string)

    # write a regex to get the genre which should return hip-hop
    genre = re.search(r'genre-(\w+(?:-\w+)*)', string)
    # # write a regex to get the words that has " -" after it
    # words_functions = re.findall(r'(\w+(?:-\w+)*) -', test)
    # dic = {"genre": genre.group(1), "gather": gather.group(1), "artist": artist.group(1)}
    dic = {"genre": None, "gather": None, "artist": None}
    if genre:
        dic["genre"] = genre.group(1).replace("_", " ")
    if gather:
        dic["gather"] = gather.group(1).replace("_", " ")
    if artist:
        dic["artist"] = artist.group(1).replace("_", " ")
    return dic

# # get all the playlists that are new
# def get_new_playlists():

#     user_playlist_info = get_user_playlists_info()
#     new_df = pd.DataFrame(user_playlist_info)
#     new_df['date'] = datetime.datetime.now()
#     # read the csv file
#     old_df = pd.read_csv('user_playlists_info.csv')

#     """Iterate though the new_df and search for matching value from the old dataframe save the index where the first value matches. the value should continue to match."""
#     # iterate through the new_df
#     user_playlist_info = get_user_playlists_info()
#     new_df = pd.DataFrame(user_playlist_info)
#     new_df['date'] = datetime.datetime.now()
#     # read the csv file
#     old_df = pd.read_csv('user_playlists_info.csv')
#     the_index = 0
#     previous_index = -1
#     for i in range(len(new_df)):
#         song_id = new_df['playlist_id'][i]
#         try:
#             # get the index of the matching value
#             index = old_df[old_df['playlist_id'] == song_id].index[0]
#             # if the index is not the previous index + 1 and it is not the first index
#             if i != previous_index+1 and i != 0:
#                 # save the index
#                 the_index = i
#             previous_index = i
#         except IndexError:
#             pass
#     changed = new_df[:the_index]

#     # replace the rows before the index with the new rows, changed
#     old_df[:the_index] = changed
#     # save the new dataframe to the csv file
#     # old_df.to_csv('user_playlists_info.csv', index=False)
#     # return all the playlits that are new
#     # store_user_playlists_info() # pause while updating the function
#     return changed

def get_new_playlists():
    """Get all the playlists that are new from the user's playlists info.

    Parameters
    ----------
    None

    Returns
    -------
    new_playlists : pd.DataFrame
        A data frame with the new playlists info and date.
    """
    # Get the user's playlists info as a data frame
    user_playlist_info = get_user_playlists_info()
    new_df = pd.DataFrame(user_playlist_info)
    # Add the current date column
    new_df['date'] = datetime.datetime.now()
    # Read the csv file as a data frame
    old_df = pd.read_csv('user_playlists_info.csv')
    # Merge the two data frames on playlist id
    merged_df = pd.merge(new_df, old_df, on='playlist_id', how='outer', indicator=True)
    # Filter the data frame to keep only the rows that are in the left data frame (new_df)
    new_playlists = merged_df[merged_df['_merge'] == 'left_only']
    # Drop the _merge column
    new_playlists.drop('_merge', axis=1, inplace=True)
    # Return the new playlists data frame
    return new_playlists


# # get all the playlists with functions hidden in the name or description
# def get_playlists_with_functions():
#     new_playlists = get_new_playlists()
#     # create a dictonary to store the playlists id with functions
#     playlists_with_functions = {}
#     # iterate through the new playlists
#     for i in range(len(new_playlists)):
#         # use gather_functions to check if the playlist name and description has functions
#         name = gather_functions(new_playlists['playlist_name'][i].lower())
#         description = gather_functions(new_playlists['playlist_description'][i].lower())
#         funciton_data = {}
#         # print(name)
#         # print(description)
#         # iterate through the dictonary and check if the value is not None
#         for key, value in name.items():
#             if value:
#                 # if both the name and description have different values for the same key set a list with both values
#                 if description[key] and description[key] != value:
#                     funciton_data[key] = [value, description[key]]
#                 else:
#                     funciton_data[key] = [value]
#             # add playlist id to the dictonary
#             # funciton_data['playlist_id'] = new_playlists['playlist_id'][i]
#         # save funciton_data to the playlists_with_functions dictonary with key as the playlist id
#         playlists_with_functions[new_playlists['playlist_id'][i]] = funciton_data
#     return playlists_with_functions

def get_playlists_with_functions():
    """Get new playlists with functions from their names and descriptions.

    Parameters
    ----------
    None

    Returns
    -------
    playlists_with_functions : dict
        A dictionary with playlist ids as keys and function data as values.
    """
    new_playlists = get_new_playlists()
    # Create a dictionary to store the playlists id with functions
    playlists_with_functions = {}
    # Iterate through the new playlists
    for i, playlist in enumerate(new_playlists):
        # Use gather_functions to check if the playlist name and description has functions
        name = gather_functions(playlist['playlist_name'].lower())
        description = gather_functions(playlist['playlist_description'].lower())
        function_data = {}
        # Iterate through the dictionary and check if the value is not None
        for key, value in name.items():
            # If both the name and description have different values for the same key set a list with both values
            if description.get(key) and description.get(key) != value:
                function_data[key] = [value, description.get(key)]
            else:
                function_data[key] = [value]
        # Save function_data to the playlists_with_functions dictionary with key as the playlist id
        playlists_with_functions[playlist['playlist_id']] = function_data
    return playlists_with_functions

# # search for aritst and return the artist id
# def search_for_artist(artist):
#     # search for the artist
#     results = sp.search(q='artist:' + artist, type='artist')
#     artist_id = results['artists']['items'][0]['id']
#     return artist_id

def search_for_artist(artist):
    """Search for an artist on Spotify and return their id.

    Parameters
    ----------
    artist : str
        The name of the artist.

    Returns
    -------
    artist_id : str or None
        The id of the artist, or None if no match is found or multiple matches are found.
    """
    # Search for the artist
    results = sp.search(q=f"artist:{artist}", type='artist')
    # Check if the search returned exactly one result
    if len(results['artists']['items']) == 1:
        # Return the id of the artist
        artist_id = results['artists']['items'][0]['id']
        return artist_id
    else:
        # Return None and print a message
        print(f"No match or multiple matches found for {artist}.")
        return None

# get the all the tracks from the artist
# def get_artist_discography(name):
#     # Get the artist's albums
#     results = sp.artist_albums(search_for_artist(name), album_type='album')
#     # Extract relevant data from the API response
#     all_tarck_ids = []
#     for album in results['items']:

#         # Get the tracks of the album
#         album_tracks = sp.album_tracks(album['id'])

#         # Extract relevant data from the API response
#         for idx, track in enumerate(album_tracks['items']):
#             print(f"Track {idx+1}: {track['name']} by {track['artists'][0]['name']}")
#             print(f"Track ID: {track['id']}")
#             all_tarck_ids.append(track['id'])
#     return all_tarck_ids

def get_artist_discography(name):
    """Get the artist's discography from Spotify and print the track names and ids.

    Parameters
    ----------
    name : str
        The name of the artist.

    Returns
    -------
    all_track_ids : list
        A list of track ids from the artist's albums.
    """
    # Get the artist's albums
    results = sp.artist_albums(search_for_artist(name), album_type='album')
    # Extract relevant data from the API response
    all_track_ids = []
    for album in results['items']:

        # Get the tracks of the album
        album_tracks = sp.album_tracks(album['id'])

        # Extract relevant data from the API response
        all_track_ids += [track['id'] for track in album_tracks['items']]
        for idx, track in enumerate(album_tracks['items']):
            print(f"Track {idx+1}: {track['name']} by {track.__name__}")
            print(f"Track ID: {track['id']}")
    return all_track_ids

def get_friends_activity_json():
    """using https://github.com/valeriangalliat/spotify-buddylist repository
    Get the friends activity from Spotify using a node.js script.

    Parameters
    ----------
    None

    Returns
    -------
    friends_activity_json : dict or None
        A dictionary containing the friends activity data, or None if an error occurs.
    """
    
    # Path to the node.js script
    path_to_script = r"C:\Users\saket\Documents\GitHub\Pyhton\Project Music\spotify api\spotify-buddylist-master\example.js"
    # path_to_script = os.path.join("C:", "Users", "saket", "Documents", "GitHub", "Pyhton", "Project Music", "spotify api", "spotify-buddylist-master", "example.js")

    while True:
        # Run the node.js script and get the output as bytes
        friends_activity_bytes = subprocess.check_output(["node", path_to_script])
        # friends_activity_json = get_friends_activity_json()
        if friends_activity_bytes != None:
            break
        else: time.sleep(60)

    # Decode the bytes to string
    friends_activity_str = friends_activity_bytes.decode("utf-8")
    # Convert the string to json object
    friends_activity_json = json.loads(friends_activity_str)
    # Return the json object
    return friends_activity_json
## get_friends_activity_json()

# create the file if it does not exist
def create_file(file_name):
    """Create a csv file if it does not exist and return the file as a pandas dataframe.

    Parameters
    ----------
    file_name : str
        The name of the csv file.

    Returns
    -------
    friends_activity : pandas dataframe
        A pandas dataframe containing the data from the csv file.
    """
    # check if the file exists
    try:
        # read the csv file
        friends_activity = pd.read_csv(file_name)
    except FileNotFoundError:
        # create a csv file
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['user_uri', 'track_uri', 'timestamp', 'current_time'])
        # read the csv file
        friends_activity = pd.read_csv(file_name)
    return friends_activity

# for  'friends_activity.csv', 'friend_activity.csv', 'recently_played_tracks.csv', 'friends_activity.sqlite'
# push the data files to github regularly
def push_to_github(files):
    """
    Description
    -----------
    Push the files to github.

    Parameters
    ----------
    files : list
        A list of files to push to github.

    Returns
    -------
    None
    """
    # list of files to push
    # commit message
    commit_message = "files updated"
    # push the files to github
    for file in files:
        subprocess.check_output(["git", "add", file])
    subprocess.check_output(["git", "commit", "-m", commit_message])
    subprocess.check_output(["git", "push"])

# this loop will keep running until we get the json response, if we get None as response then it will keep running
def keep_trying_until_get_friends_activity_json():
    """
    Description
    -----------
    Keep trying to get the friends activity json until we get it.
    """
    while True:
        friends_activity_json = get_friends_activity_json()
        if friends_activity_json != None:
            break
        else: time.sleep(60)

def user_id_to_user_uri(users = ["gntab9tp1cc5qipthodlvvsm3"]):
    """
    Description
    -----------
    Convert a list of user ids to user uris.

    Parameters
    ----------
    users : list
        A list of user ids.

    Returns
    -------
    user_uris : list
        A list of user uris.
    """
    user_ids = ["spotify:user:" + user_id for user_id in user_ids]
    return user_ids


# define a function to store the user data to a database
def store_user_data_to_database(friends_activity_json, database_name='friends_activity.db'):
    '''
    This function is divided into 2 parts:
    - Create the database and tables if they do not exist
    - Loop through the JSON data of friends' activity and store the data to the database
    '''

    '''
    # Create the database and tables if they do not exist
    - connect to the database with the given name or create a new one if it does not exist
    - create a table for users with columns for user_id, user_url, user_name and user_image_url
    - create a table for albums with columns for album_id, album_uri and album_name
    - create a table for artists with columns for artist_id, artist_uri and artist_name
    - create a table for tracks with columns for track_id, track_uri, track_name, track_image_url, album_id and artist_id
    - create a table for context with columns for context_id, context_uri, context_name and context_index
    - create a table for streamings with columns for user_id, track_id and timestam
    '''

    # connect to the database with the given name or create a new one if it does not exist
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()

    # create a table for users with columns for user_id, user_url, user_name and user_image_url
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        user_uri TEXT NOT NULL,
        user_name TEXT NOT NULL,
        user_image_url TEXT NOT NULL
    )
    ''')

    # create a table for albums with columns for album_id, album_uri and album_name
    cur.execute('''CREATE TABLE IF NOT EXISTS albums(
        album_id INTEGER PRIMARY KEY,
        album_uri TEXT NOT NULL,
        album_name TEXT NOT NULL
    )
    ''')

    # create a table for artists with columns for artist_id, artist_uri and artist_name
    cur.execute('''CREATE TABLE IF NOT EXISTS artists(
        artist_id INTEGER PRIMARY KEY,
        artist_uri TEXT NOT NULL,
        artist_name TEXT NOT NULL
    )
    ''')

    # create a table for tracks with columns for track_id, track_uri, track_name, track_image_url, album_id and artist_id
    # add foreign key constraints to reference the album_id and artist_id from the albums and artists tables respectively
    cur.execute('''CREATE TABLE IF NOT EXISTS tracks (
        track_id INTEGER PRIMARY KEY,
        track_uri TEXT NOT NULL,
        track_name TEXT NOT NULL,
        track_image_url TEXT NOT NULL,
        album_id INTEGER NOT NULL,
        artist_id INTEGER NOT NULL,
        FOREIGN KEY (album_id) REFERENCES albums(album_id),
        FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
    )
    ''')

    # create a table for context with columns for context_id, context_uri, context_name and context_index
    cur.execute('''CREATE TABLE IF NOT EXISTS context(
        context_id INTEGER PRIMARY KEY,
        context_uri TEXT NOT NULL,
        context_name TEXT NOT NULL,
        context_index INTEGER NOT NULL
    )
    ''')

    # create a table for streamings with columns for user_id, track_id and timestamp
    # add foreign key constraints to reference the user_id and track_id from the users and tracks tables respectively
    cur.execute('''CREATE TABLE IF NOT EXISTS streamings(
        user_id INTEGER NOT NULL,
        track_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (track_id) REFERENCES tracks(track_id)
    )
    '''
    )
    '''
    
    # Loop through the JSON data of friends' activity and store the data to the database
    - loop through the JSON data of friends' activity
    - get the user data from the JSON object
    - check if the user already exists in the users table by querying the user_url column
    - if the query returns None, it means the user does not exist in the table
        - insert a new row into the users table with the user data and get the generated user_id value
    - if the query returns a tuple, it means the user already exists in the table and extract the first element of the tuple as the user_id value
    '''
    # loop through the JSON data of friends' activity
    for data in friends_activity_json['friends']:
        # get the user data from the JSON object
        # print(data)
        user_url = data['user']['uri']
        user_name = data['user']['name']
        user_image_url = data['user']['imageUrl']

        # check if the user already exists in the users table by querying the user_url column
        cur.execute("SELECT user_id FROM users WHERE user_url = ?", (user_url,))
        user_id = cur.fetchone()

        # if the query returns None, it means the user does not exist in the table
        if user_id is None:
            # insert a new row into the users table with the user data and get the generated user_id value
            cur.execute("INSERT INTO users (user_url, user_name, user_image_url) VALUES (?, ?, ?)", (user_url, user_name, user_image_url))
            conn.commit()
            user_id = cur.lastrowid
        else:
            # if the query returns a tuple, it means the user already exists in the table and extract the first element of the tuple as the user_id value
            user_id = user_id[0]

        # get the album data from the JSON object
        album_uri = data['track']['album']['uri']
        album_name = data['track']['album']['name']

        # check if the album already exists in the albums table by querying the album_uri column
        cur.execute("SELECT album_id FROM albums WHERE album_uri = ?", (album_uri,))
        album_id = cur.fetchone()

        # if the query returns None, it means the album does not exist in the table
        if album_id is None:
            # insert a new row into the albums table with the album data and get the generated album_id value
            cur.execute("INSERT INTO albums (album_uri, album_name) VALUES (?, ?)", (album_uri, album_name))
            conn.commit()
            album_id = cur.lastrowid
        else:
            # if the query returns a tuple, it means the album already exists in the table and extract the first element of the tuple as the album_id value
            album_id = album_id[0]

        # get the artist data from the JSON object
        artist_uri = data['track']['artist']['uri']
        artist_name = data['track']['artist']['name']

        # check if the artist already exists in the artists table by querying the artist_uri column
        cur.execute("SELECT artist_id FROM artists WHERE artist_uri = ?", (artist_uri,))
        artist_id = cur.fetchone()

        # if the query returns None, it means the artist does not exist in the table
        if artist_id is None:
            # insert a new row into the artists table with the artist data and get the generated artist_id value
            cur.execute("INSERT INTO artists (artist_uri, artist_name) VALUES (?, ?)", (artist_uri, artist_name))
            conn.commit()
            artist_id = cur.lastrowid
        else:
            # if the query returns a tuple, it means the artist already exists in the table and extract the first element of the tuple as the artist_id value
            artist_id = artist_id[0]

        # get the track data from the JSON object
        track_uri = data['track']['uri']
        track_name = data['track']['name']
        track_image_url = data['track']['imageUrl']

        # check if the track already exists in the tracks table by querying the track_uri column
        cur.execute("SELECT track_id FROM tracks WHERE track_uri = ?", (track_uri,))
        track_id = cur.fetchone()

        # if the query returns None, it means the track does not exist in the table
        if track_id is None:
            # insert a new row into the tracks table with the track data and get the generated track_id value
            cur.execute("INSERT INTO tracks (track_uri, track_name, track_image_url, album_id, artist_id) VALUES (?, ?, ?, ?, ?)", (track_uri, track_name, track_image_url, album_id, artist_id))
            conn.commit()
            track_id = cur.lastrowid
        else:
            # if the query returns a tuple, it means the track already exists in the table and extract the first element of the tuple as the track_id value
            track_id = track_id[0]

        # get the context data from the JSON object
        context_uri = data['track']['context']['uri']
        context_name = data['track']['context']['name']
        context_index = data['track']['context']['index']

        # check if the context already exists in the context table by querying the context_uri column
        cur.execute("SELECT context_id FROM context WHERE context_uri = ?", (context_uri,))
        context_id = cur.fetchone()

        # if the query returns None, it means the context does not exist in the table
        if context_id is None:
            # insert a new row into the context table with the context data and get the generated context_id value
            cur.execute("INSERT INTO context (context_uri, context_name, context_index) VALUES (?, ?, ?)", (context_uri, context_name, context_index))
            conn.commit()
            context_id = cur.lastrowid
        else:
            # if the query returns a tuple, it means the context already exists in the table and extract the first element of the tuple as the context_id value
            context_id = context_id[0]

        # get the timestamp data from the JSON object
        timestamp = data['timestamp']

        # check if there is already a streaming with the same timestamp in the streamings table by querying the timestamp column
        cur.execute("SELECT * FROM streamings WHERE timestamp = ?", (timestamp,))
        streaming = cur.fetchone()

        # if the query returns None, it means there is no streaming with the same timestamp in the table
        if streaming is None:
            # insert a new row into the streamings table with the user_id, track_id and timestamp values
            cur.execute("INSERT INTO streamings (user_id, track_id, timestamp) VALUES (?, ?, ?)", (user_id, track_id, timestamp))
            conn.commit()

def print_the_data_from_the_database():
    '''
    This function prints:
    - all the data from the users table
    - all the data from the albums table
    - all the data from the artists table
    - all the data from the tracks table
    '''

    #connect to the database
    conn = sqlite3.connect('friends_activity.db')
    cur = conn.cursor()

    # define a function that takes a table name as an argument and prints all the data from that table
    def print_table_data(table_name):
        # select all the data from the table
        cur.execute(f"SELECT * FROM {table_name}")
        data = cur.fetchall()

        # print the table name and the data
        # print(f"{table_name.capitalize()}:")
        for row in data:
            print(row)
            # break

    # call the function for each table
    print("user_id, user_uri, user_name, user_image_url")
    print_table_data("users")
    print("album_id, album_uri, album_name")
    print_table_data("albums")
    print("artist_id, artist_uri, artist_name")
    print_table_data("artists")
    print("track_id, track_uri, track_name, track_image_url, album_id, artist_id")
    print_table_data("tracks")
    print("context_id, context_uri, context_name, context_index")
    print_table_data("context")
    print("streaming_id, user_id, track_id, timestamp")
    print_table_data("streamings")

# define a function that takes a user_id as an argument and returns all the details about that user from the database
def get_user_details(user_id):
    # connect to the database
    conn = sqlite3.connect('friends_activity.db')
    cur = conn.cursor()
    # create an empty dictionary to store the user details
    user_details = {}
    # query the users table for the user data
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_data = cur.fetchone()
    # if the query returns None, it means there is no user with that id in the table
    if user_data is None:
        return None
    # otherwise, unpack the user data and store it in the dictionary
    else:
        user_id, user_url, user_name, user_image_url = user_data
        user_details['user_id'] = user_id
        user_details['user_url'] = user_url
        user_details['user_name'] = user_name
        user_details['user_image_url'] = user_image_url
        # create an empty list to store the streamings of the user
        user_details['streamings'] = []
        # query the streamings table for the streamings of the user
        cur.execute("SELECT * FROM streamings WHERE user_id = ?", (user_id,))
        streamings_data = cur.fetchall()
        # loop through the streamings data and get the track and context details for each streaming
        for streaming_data in streamings_data:
            # create an empty dictionary to store the streaming details
            streaming_details = {}
            # unpack the streaming data and store it in the dictionary
            streaming_user_id, track_id, timestamp = streaming_data
            streaming_details['timestamp'] = timestamp
            # query the tracks table for the track data
            cur.execute("SELECT * FROM tracks WHERE track_id = ?", (track_id,))
            track_data = cur.fetchone()
            # unpack the track data and store it in the dictionary
            track_id, track_uri, track_name, track_image_url, album_id, artist_id = track_data
            streaming_details['track_uri'] = track_uri
            streaming_details['track_name'] = track_name
            streaming_details['track_image_url'] = track_image_url
            # query the albums table for the album data
            cur.execute("SELECT * FROM albums WHERE album_id = ?", (album_id,))
            album_data = cur.fetchone()
            # unpack the album data and store it in the dictionary
            album_id, album_uri, album_name = album_data
            streaming_details['album_uri'] = album_uri
            streaming_details['album_name'] = album_name
            # query the artists table for the artist data
            cur.execute("SELECT * FROM artists WHERE artist_id = ?", (artist_id,))
            artist_data = cur.fetchone()
            # unpack the artist data and store it in the dictionary
            artist_id, artist_uri, artist_name = artist_data
            streaming_details['artist_uri'] = artist_uri
            streaming_details['artist_name'] = artist_name
            # query the context table for the context data
            cur.execute("SELECT * FROM context WHERE context_uri IN (SELECT context_uri FROM tracks WHERE track_id = ?)", (track_id,))
            context_data = cur.fetchone()
            # unpack the context data and store it in the dictionary
            context_id, context_uri, context_name, context_index = context_data
            streaming_details['context_uri'] = context_uri
            streaming_details['context_name'] = context_name
            streaming_details['context_index'] = context_index
            # append the streaming details to the list of streamings of the user
            user_details['streamings'].append(streaming_details)
        # return the user details dictionary 
        return user_details

# import the rich library
from rich import print
from rich.table import Table
from rich.console import Console
# import the datetime library
from datetime import datetime

# define a function that takes a number as a parameter and prints the last n songs by each user and the songs in details with all the correct labels
def print_last_played_songs(n):
    # connect to the database
    conn = sqlite3.connect('friends_activity.db')
    cur = conn.cursor()
    # query the users table for all the user_ids and user_names
    cur.execute("SELECT user_id, user_name FROM users")
    users = cur.fetchall()
    # create a table object with columns for streaming details
    table = Table(show_header=True, header_style="bold magenta")
    # sort the table by timestamp in ascending order
    # table = table.sort_values(by="Time Since Played")
    table.add_column("User")
    table.add_column("Time Since Played")
    table.add_column("Track URI")
    table.add_column("Track Name")
    table.add_column("Album Name")
    table.add_column("Artist Name")
    # loop through the users and add their streamings to the table rows
    for user in users:
        # extract the user_id and user_name from the tuple
        user_id, user_name = user
        # query the streamings table for the last n streamings of the user ordered by timestamp in descending order
        cur.execute("SELECT track_id, timestamp FROM streamings WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, n))
        streamings = cur.fetchall()
        # loop through the streamings and add their details to the table rows
        for streaming in streamings:
            # extract the track_id and timestamp from the tuple
            track_id, timestamp = streaming
            # convert the timestamp to a datetime object
            time_since_played = time_variation(int(timestamp))
            # query the tracks table for the track data
            cur.execute("SELECT track_uri, track_name, track_image_url, album_id, artist_id FROM tracks WHERE track_id = ?", (track_id,))
            track_data = cur.fetchone()
            # unpack the track data and store it in variables
            track_uri, track_name, track_image_url, album_id, artist_id = track_data
            # query the albums table for the album data
            cur.execute("SELECT album_uri, album_name FROM albums WHERE album_id = ?", (album_id,))
            album_data = cur.fetchone()
            # unpack the album data and store it in variables
            album_uri, album_name = album_data
            # query the artists table for the artist data
            cur.execute("SELECT artist_uri, artist_name FROM artists WHERE artist_id = ?", (artist_id,))
            artist_data = cur.fetchone()
            # unpack the artist data and store it in variables
            artist_uri, artist_name = artist_data
            # query the context table for the context data
            cur.execute("SELECT context_uri, context_name, context_index FROM context WHERE context_uri IN (SELECT context_uri FROM tracks WHERE track_id = ?)", (track_id,))
            context_data = cur.fetchone()
            # unpack the context data and store it in variables
            context_uri, context_name, context_index = context_data
            # add a row to the table with the streaming details 
            table.add_row(user_name, time_since_played, track_uri, track_name, album_name, artist_name)
    # create a console object to print the table 
    console = Console()
    console.print(table)

def time_variation(timestamp):
        # get the current time in seconds
    current_time = time.time()
    # convert it to milliseconds by multiplying by 1000
    current_time_in_millis = int(current_time * 1000)
    difference = current_time_in_millis- timestamp
    minutes = difference/60000
    # format the time difference as a string
    if minutes < 1:
        time_since_played = "Just now"
    elif minutes == 1:
        time_since_played = "1 minute ago"
    elif minutes < 60:
        time_since_played = f"{round(minutes)} minutes ago"
    elif minutes == 60:
        time_since_played = "1 hour ago"
    elif minutes%60 == 0 and minutes < 24*60:
        time_since_played = f"{minutes/60} hours ago"
    elif minutes >  60 and minutes < 24*60:
        time_since_played = f"{round(minutes/60)} hr {round(minutes%60)} min ago"
    elif minutes > 24*60:
        print(("I am liike what"))
        time_since_played = f"{round(minutes//(24*60))} days ago"
    return time_since_played



"""My streaming history"""
# define a function to store streaming activity data to a database
def store_my_streaming_data_to_database(database_name='MyStreamingHistory.db'):
    '''
    This function is divided into 2 parts:
    - Create the database and tables if they do not exist
    - Loop through the JSON data of streaming activity and store the data to the database
    '''

    # connect to the database with the given name or create a new one if it does not exist
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()

    # create a table for albums with columns for album_id, album_uri, album_name, album_type, release_date, total_tracks and image_url
    cur.execute('''CREATE TABLE IF NOT EXISTS albums (
        album_id INTEGER PRIMARY KEY,
        album_uri TEXT NOT NULL,
        album_name TEXT NOT NULL,
        album_type TEXT NOT NULL,
        release_date TEXT NOT NULL,
        total_tracks INTEGER NOT NULL,
        image_url TEXT NOT NULL
        )
    ''')

    # create a table for artists with columns for artist_id, artist_uri and artist_name
    cur.execute('''CREATE TABLE IF NOT EXISTS artists(
        artist_id INTEGER PRIMARY KEY,
        artist_uri TEXT NOT NULL,
        artist_name TEXT NOT NULL
        )
    ''')

    # create a table for tracks with columns for track_id, track_uri, track_name, track_number, duration_ms, disc_number, popularity, preview_url, album_id and artist_id
    # add foreign key constraints to reference the album_id and artist_id from the albums and artists tables respectively
    cur.execute('''CREATE TABLE IF NOT EXISTS tracks (
        track_id INTEGER PRIMARY KEY,
        track_uri TEXT NOT NULL,
        track_name TEXT NOT NULL,
        track_number INTEGER NOT NULL,
        duration_ms INTEGER NOT NULL,
        disc_number INTEGER NOT NULL,
        popularity INTEGER NOT NULL,
        preview_url TEXT,
        album_id INTEGER NOT NULL,
        artist_id INTEGER NOT NULL,
        FOREIGN KEY (album_id) REFERENCES albums(album_id),
        FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
        )
    ''')

    # create a table for streamings with columns for track_id and played_at
    # add foreign key constraints to reference the track_id from the tracks table
    cur.execute('''CREATE TABLE IF NOT EXISTS streamings(
        track_id INTEGER NOT NULL,
        played_at TEXT NOT NULL,
        FOREIGN KEY (track_id) REFERENCES tracks(track_id)
        )
    ''')
    streaming_activity_json = parse_streaming_history()
    # loop through the JSON data of streaming activity
    for data in streaming_activity_json:
        # get the album data from the JSON object
        album_uri = data['album_uri']
        album_name = data['album_name']
        album_type = data['album_type']
        release_date = data['release_date']
        total_tracks = data['total_tracks']
        image_url = data['image_url']

        # check if the album already exists in the albums table by querying the album_uri column
        cur.execute("SELECT album_id FROM albums WHERE album_uri = ?", (album_uri,))
        album_id = cur.fetchone()

        # if the query returns None, it means the album does not exist in the table
        if album_id is None:
            # insert a new row into the albums table with the album data and get the generated album_id value
            cur.execute("INSERT INTO albums (album_uri, album_name, album_type, release_date, total_tracks, image_url) VALUES (?, ?, ?, ?, ?, ?)", (album_uri, album_name, album_type, release_date, total_tracks, image_url))
            conn.commit()
            album_id = cur.lastrowid
        else:
            # if the query returns a tuple, it means the album already exists in the table and extract the first element of the tuple as the album_id value
            album_id = album_id[0]

        # get the artist data from the JSON object
        artist_uris = data['artist_uris']
        artist_names = data['artist_names']

        # loop through the artist_uris and artist_names lists
        for i in range(len(artist_uris)):
            # get the artist_uri and artist_name at index i
            artist_uri = artist_uris[i]
            artist_name = artist_names[i]

            # check if the artist already exists in the artists table by querying the artist_uri column
            cur.execute("SELECT artist_id FROM artists WHERE artist_uri = ?", (artist_uri,))
            artist_id = cur.fetchone()

            # if the query returns None, it means the artist does not exist in the table
            if artist_id is None:
                # insert a new row into the artists table with the artist data and get the generated artist_id value
                cur.execute("INSERT INTO artists (artist_uri, artist_name) VALUES (?, ?)", (artist_uri, artist_name))
                conn.commit()
                artist_id = cur.lastrowid
            else:
                # if the query returns a tuple, it means the artist already exists in the table and extract the first element of the tuple as the artist_id value
                artist_id = artist_id[0]

        # get the track data from the JSON object
        track_uri = data['track_uri']
        track_name = data['track_name']
        track_number = data['track_number']
        duration_ms = data['duration_ms']
        disc_number = data['disc_number']
        popularity = data['popularity']
        preview_url = data['preview_url']

        # check if the track already exists in the tracks table by querying the track_uri column
        cur.execute("SELECT track_id FROM tracks WHERE track_uri = ?", (track_uri,))
        track_id = cur.fetchone()

        # if the query returns None, it means the track does not exist in the table
        if track_id is None:
            # insert a new row into the tracks table with the track data and get the generated track_id value
            cur.execute("INSERT INTO tracks (track_uri, track_name, track_number, duration_ms, disc_number, popularity, preview_url, album_id, artist_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (track_uri, track_name, track_number, duration_ms, disc_number, popularity, preview_url, album_id, artist_id))
            conn.commit()
            track_id = cur.lastrowid
        else:
            # if the query returns a tuple, it means the track already exists in the table and extract the first element of the tuple as the track_id value
            track_id = track_id[0]

        # get the played_at data from the JSON object
        played_at = data['played_at']
        # played_at = data['played_at']
        parsed_time = parser.parse(played_at)
        played_at = parsed_time.timestamp() * 1000

        # check if there is already a streaming with the same played_at in the streamings table by querying the played_at column
        cur.execute("SELECT * FROM streamings WHERE played_at = ?", (played_at,))
        streaming = cur.fetchone()

        # if the query returns None, it means there is no streaming with the same played_at in the table
        if streaming is None:
            # insert a new row into the streamings table with the track_id and played_at values
            cur.execute("INSERT INTO streamings (track_id, played_at) VALUES (?, ?)", (track_id, played_at))
            conn.commit()

    # close the connection
    conn.close()

# define a function that prints the database with some parameters
def print_my_database(database_name='MyStreamingHistory.db', table_name=None, limit=None, order_by=None, print_full_preview_url=False, max_lenght_each_values=50):
    '''
    This function prints the database with some parameters
    - database_name: the name of the database file to connect to
    - table_name: the name of the table to print, if None, print all tables
    - limit: the number of rows to print, if None, print all rows
    - order_by: the column name to sort the rows by, if None, use the default order
    '''

    # connect to the database with the given name
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()

    # get the list of table names from the database
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = [row[0] for row in cur.fetchall()]

    # if table_name is None or not valid, print all tables
    if table_name is None or table_name not in table_names:
        for table in table_names:
            # print the table name
            print(f"Table: {table}")

            # get the column names from the table
            cur.execute(f"PRAGMA table_info({table})")
            column_names = [row[1] for row in cur.fetchall()]

            # print the column names as headers
            print(*column_names, sep='\t')

            # construct the SQL query to select rows from the table
            sql = f"SELECT * FROM {table}"

            # if order_by is not None and valid, add it to the query
            if order_by is not None and order_by in column_names:
                sql += f" ORDER BY {order_by}"

            # if limit is not None and positive, add it to the query
            if limit is not None and limit > 0:
                sql += f" LIMIT {limit}"

            # execute the query and fetch the rows
            cur.execute(sql)
            rows = cur.fetchall()

            # print the rows as values
            for row in rows:
                # if print_full_preview_url is False, replace the preview_url column with a shorter version
                if not print_full_preview_url and 'preview_url' in column_names:
                    # get the index of the preview_url column
                    index = column_names.index('preview_url')

                    # replace the preview_url column with a shorter version
                    row = row[:index] + ('...',) + row[index+1:]
                # don't print more than 50 each row
                row = [str(value)[:50] for value in row]
                print(*row, sep='\t')

            # print a blank line after each table
            print()

    else:
        # if table_name is valid, print only that table
        # print the table name
        print(f"Table: {table_name}")

        # get the column names from the table
        cur.execute(f"PRAGMA table_info({table_name})")
        column_names = [row[1] for row in cur.fetchall()]

        # print the column names as headers
        print(*column_names, sep='\t')

        # construct the SQL query to select rows from the table
        sql = f"SELECT * FROM {table_name}"

        # if order_by is not None and valid, add it to the query
        if order_by is not None and order_by in column_names:
            sql += f" ORDER BY {order_by}"

        # if limit is not None and positive, add it to the query
        if limit is not None and limit > 0:
            sql += f" LIMIT {limit}"

        # execute the query and fetch the rows
        cur.execute(sql)
        rows = cur.fetchall()

        # print the rows as values
        for row in rows:
            print(*row, sep='\t')

    # close the connection
    conn.close()

# def display_data_from_database(database_name='MyStreamingHistory.db', table_name=None, columns=None, rows=None):
#     '''
#     This function is used to display the data from a given database and table.
#     It can also filter the data by specifying the columns and rows to show.
#     If no table name is given, it will show all the tables in the database.
#     If no columns are given, it will show all the columns in the table.
#     If no rows are given, it will show all the rows in the table.

#     Parameters:
#     - database_name: The name of the database file to connect to.
#     - table_name: The name of the table to display the data from. If None, all tables in the database will be shown.
#     - columns: A list of column names to display. If None, all columns will be shown.
#     - rows: A list of values to filter the data rows. If None, no row filtering will be applied.

#     Returns:
#     - None
#     '''

#     # import pandas and sqlite3 modules
#     import pandas as pd
#     import sqlite3

#     # connect to the database with the given name
#     conn = sqlite3.connect(database_name)
#     cur = conn.cursor()

#     # if no table name is given, show all the tables in the database
#     if table_name is None:
#         # query the sqlite_master table to get the names of all the tables
#         cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
#         tables = cur.fetchall()
#         # loop through the tables and display their names
#         print(f"Tables in {database_name}:")
#         for table in tables:
#             print(table[0])
#         # close the connection
#         conn.close()
#         # return None
#         return None

#     # if a table name is given, show the data from that table
#     else:
#         # if no columns are given, show all the columns in the table
#         if columns is None:
#             # query the PRAGMA table_info to get the names of all the columns
#             cur.execute(f"PRAGMA table_info({table_name})")
#             columns = cur.fetchall()
#             # extract the column names from the query result
#             column_names = [column[1] for column in columns]
#             # create a SQL query to select all the columns from the table
#             sql_query = f"SELECT * FROM {table_name}"
#             # if rows are given, add a WHERE clause to filter by row values
#             if rows is not None:
#                 # create a list of conditions for each row value
#                 conditions = [f"{column_names[i]} = '{rows[i]}'" for i in range(len(rows))]
#                 # join the conditions with AND operator
#                 where_clause = " AND ".join(conditions)
#                 # add the WHERE clause to the SQL query
#                 sql_query += f" WHERE {where_clause}"
#             # execute the SQL query and fetch the data as a pandas dataframe
#             df = pd.read_sql_query(sql_query, conn)
#             # display the dataframe
#             print(df)
#             # close the connection
#             conn.close()
#             # return None
#             return None

#         # if columns are given, show only those columns in the table
#         else:
#             # create a SQL query to select only those columns from the table
#             sql_query = f"SELECT {', '.join(columns)} FROM {table_name}"
#             # if rows are given, add a WHERE clause to filter by row values
#             if rows is not None:
#                 # create a list of conditions for each row value
#                 conditions = [f"{columns[i]} = '{rows[i]}'" for i in range(len(rows))]
#                 # join the conditions with AND operator
#                 where_clause = " AND ".join(conditions)
#                 # add the WHERE clause to the SQL query
#                 sql_query += f" WHERE {where_clause}"
#             # execute the SQL query and fetch the data as a pandas dataframe
#             df = pd.read_sql_query(sql_query, conn)
#             # display the dataframe
#             print(df)
#             # close the connection
#             conn.close()
#             # return None
#             return None


def count_down(time_in_sec):
    '''
    This function takes a time in seconds as an argument and prints a countdown
    '''
    # loop through the time in seconds
    for i in range(time_in_sec, 0, -1):
        # print the time in seconds
        print(i)
        # wait one second
        time.sleep(1)


# if __name__ == "__main__":
#     while True:
#         try:
#             store_user_data_to_database(get_friends_activity_json())
#             # print_the_data_from_the_database()
#             print_last_played_songs(1)
#             count_down(30)
#         # print the error message if the program fails
#         except Exception as e:
#             print(e)
#             count_down(30)
#         except KeyboardInterrupt:
#             break
#         except:
#             print("Something went wrong")
#             count_down(30)

from threading import Thread, Timer
import time


from typing import Callable, Generator

def count_down(time_in_sec: int, callback: Callable = None) -> Generator[int, None, None]:
    '''
    This function takes a time in seconds as an argument and yields a countdown.

    Optionally, it can execute a callback function after each countdown value.

    >>> list(count_down(3))
    [3, 2, 1]
    >>> list(count_down(3, print))
    3
    2
    1
    [None, None, None]
    '''

    # yield the time in seconds
    for i in range(time_in_sec, 0, -1):
        yield i
        # execute the callback if given
        if callback:
            callback()
        # wait one second
        time.sleep(1)


def count_down(time_in_sec):
    '''
    This function takes a time in seconds as an argument and prints a countdown
    '''
    # loop through the time in seconds
    for i in range(time_in_sec, 0, -1):
        # print the time in seconds
        print(i)
        # wait one second
        time.sleep(1)



def count_down(time_in_sec):
    '''
    This function takes a time in seconds as an argument and prints a countdown
    '''
    # loop through the time in seconds
    for i in range(time_in_sec, 0, -1):
        # print the time in seconds
        print(i)
        # wait one second
        time.sleep(1)

def store_user_data():
    try:
        store_user_data_to_database(get_friends_activity_json())
        # print_the_data_from_the_database()
        print_last_played_songs(1)
        # schedule the next call after 30 seconds
        Timer(30, store_user_data).start()
    except Exception as e:
        print(e)
        # print a message indicating retrying
        print("Retrying store_user_data in 30 seconds...")
        # schedule the next call after 30 seconds
        Timer(30, store_user_data).start()

def store_streaming_data():
    try:
        store_my_streaming_data_to_database(database_name='MyStreamingHistory.db')
        # schedule the next call after 8 minutes
        print_the_data_from_the_database()
        Timer(480, store_streaming_data).start()
    except Exception as e:
        print(e)
        # print a message indicating retrying
        print("Retrying store_streaming_data in 8 seconds...")
        # schedule the next call after 8 seconds
        Timer(8, store_streaming_data).start()

# if __name__ == "__main__":
#     # start the first thread as daemon
#     Thread(target=store_user_data, daemon=True).start()
#     # start the second thread as daemon
#     Thread(target=store_streaming_data, daemon=True).start()
#     # keep the main thread alive until Ctrl + C is pressed
#     user_input = None # a variable to store the user input
#     try:
#         # read from the standard input
#         user_input = input()
#     except EOFError:
#         # display the database if Ctrl + D is pressed
#         display_data_from_database()
#         # print_my_database()

if __name__ == "__main__":
    display_data_from_database()
    print_my_database()