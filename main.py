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

# set the client_ID, client_SECRET, redirect_uri and username for the spotify api authentication
client_ID = '4e1c1626b9e04c0fba6d8f14d31ab3e6'
client_SECRET = '607dd5362f9d4f44b33361eca5aa81b8'   
redirect_uri = 'http://127.0.0.1:9090'
username = 'rt47etgc6xpwhhhb8575rth83'

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

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# returns a spotipy object with the given scope
def get_spotify_token(scope):
    client_credentials_manager.get_access_token(as_dict=False)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

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
    results = playlist_read_private.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# returns the recently played tracks
def get_recently_played_tracks(limit=50):
    recently_played = user_read_recently_played.current_user_recently_played(limit=limit)
    return recently_played

# returns the top 50 artists played by the user
def add_to_playlist(playlist_id, list_of_tracks):
    splity_split = split_with_no(list_of_tracks, 100)
    for hundred_lis in splity_split:
        playlist_modify_private.user_playlist_add_tracks(user=username, playlist_id=playlist_id, tracks=hundred_lis)

# splits the list into sublists of size 100
def split_with_no(list, No):
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
    top_tracks = token.current_user_top_tracks(limit=limit)
    return top_tracks

# returns a datetime object from the given timestamp
def timestamp_to_time(timestamp):
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
    # iterate through all the keys in the track_json try to get the value of the key, else set the value to None
    track_info = {}
    for key in track_dict.keys():
        try:
            track_info[key] = track_json[key]
        except:
            track_info[key] = None
    return track_info

# returns a list of dictionaries with the track info for each track
def get_recently_played_tracks_info():
    # list to store the recently played tracks
    recently_played_tracks = []
    # get the recently played tracks
    recently_played = get_recently_played_tracks()
    # iterate through all the recently played tracks
    for i in range(len(recently_played['items'])):
        # get the track info
        track = recently_played['items'][i]['track']
        # create a dictionary to store the track info
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
            'artist_id': track['artists'][0]['id'],
            'played_at': recently_played['items'][i]['played_at']
        }
        # print the track info
        song_name = track['name']
        # print the track time and name
        # print(recently_played['items'][i]['played_at'], song_name)

        recently_played_tracks.append(track_info)
    return recently_played_tracks

# stores the recently played tracks in a csv file
def store_recently_played_tracks():
    # get the recently played tracks
    recently_played_tracks = get_recently_played_tracks_info()
    # create a dataframe from the stored recently played tracks
    old_recently_played_tracks = pd.read_csv(recently_played_file_name)
    # create a dataframe from the list of recently played tracks
    new_recently_played_tracks = pd.DataFrame(recently_played_tracks)
    # get the last played track from the old_recently_played_tracks
    last_played_at = old_recently_played_tracks['played_at'].iloc[-1]
    # reverse the new_recently_played_tracks
    new_recently_played_tracks = new_recently_played_tracks.iloc[::-1]

    # iterate though all the new_recently_played_tracks and find the one which is closest to the last_played_at
    for i in range(len(new_recently_played_tracks)):
        # get the difference between the last_played_at and the current track's played_at in hours
        diff = (timestamp_to_time(last_played_at) - timestamp_to_time(new_recently_played_tracks['played_at'].iloc[i])).total_seconds() / 3600
        # if the difference is negative, then the current track is the one which was last played
        if diff < 0:
            # get the index of the new_recently_played_tracks
            index = i
            # start the new_recently_played_tracks from the index
            new_recently_played_tracks = new_recently_played_tracks.iloc[index:]
            # iterate through all the new_recently_played_tracks and print the track name and time
            print("Newly added tracks:")
            for j in range(len(new_recently_played_tracks)):
                print(new_recently_played_tracks['played_at'].iloc[j], new_recently_played_tracks['track_name'].iloc[j])
            # add the new_recently_played_tracks to the old_recently_played_tracks, use .concat() to avoid the index being repeated
            old_recently_played_tracks = pd.concat([old_recently_played_tracks, new_recently_played_tracks])
            # save the old_recently_played_tracks to the csv file
            old_recently_played_tracks.to_csv(recently_played_file_name, index=False)
            break

# function to get the spotify token for the given scope
def get_top_tracks(limit=200):
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

# returns the user's top artists in a list
def get_top_artists_info(limit=200):
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
    # get the token for the user-library-read scope
    # get the user's library data
    library = user_library_read.current_user_saved_tracks(limit=limit)

    # convert the library data to a dataframe
    library_df = pd.DataFrame(library)
    return library_df

# returns a list of dictionaries containing the user's playlists
def get_user_playlists():
    user_playlists = playlist_read_private.current_user_playlists(limit=50)
    return user_playlists

# returns a list of dictionaries containing the user's playlists
def store_user_playlists_info():
    user_playlists_info = get_user_playlists_info()
    user_playlists_info_df = pd.DataFrame(user_playlists_info)
    user_playlists_info_df.to_csv('user_playlists_info.csv', index=False)

# returns the tracks in a playlist in a dictionary
def get_user_playlist_tracks(playlist_id):
    user_playlist_tracks = playlist_read_private.user_playlist_tracks(playlist_id)
    return user_playlist_tracks

# returns the tracks in a playlist in a list of dictionaries
def get_user_playlist_tracks_info(playlist_id):
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
    # returns a json of recommended tracks according to the seed artists, genres and tracks
    recommendations = user_top_read.recommendations(seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks)
    return recommendations

# get important info from recommendations json
def get_recommendations_info(seed_artists, seed_genres, seed_tracks):
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
    saved_albums = user_library_read.current_user_saved_albums()
    return saved_albums

# returns the user's saved shows in a list
def get_saved_shows():
    saved_shows = user_library_read.current_user_saved_shows()
    return saved_shows

# returns the user's saved episodes in a list
def get_saved_episodes():
    saved_episodes = user_library_read.current_user_saved_episodes()
    return saved_episodes

# returns the user's library tracks in a list
def get_library_info(limit):
    # get the user's library data
    library = user_library_read.current_user_saved_tracks(limit=limit)
    # convert the library data to a dataframe
    library_df = pd.DataFrame(library)
    return library_df

# Define a function to get the value of a nested key from a dictionary
def get_nested_value(dictionary, keys, default=''):
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

# store the user's playlists information in a csv file
def store_user_playlists_info():    
    user_playlists_info = get_user_playlists_info()
    df = pd.DataFrame(user_playlists_info)
    # add a column with the current date and time
    df['date'] = datetime.datetime.now()
    df.to_csv('user_playlists_info.csv', index=False)

# get the commands stored in the playlist name or description
def gather_functions(string):
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

# get all the playlists that are new
def get_new_playlists():
    
    user_playlist_info = get_user_playlists_info()
    new_df = pd.DataFrame(user_playlist_info)
    new_df['date'] = datetime.datetime.now()
    # read the csv file
    old_df = pd.read_csv('user_playlists_info.csv')

    """Iterate though the new_df and search for matching value from the old dataframe save the index where the first value matches. the value should continue to match."""
    # iterate through the new_df
    user_playlist_info = get_user_playlists_info()
    new_df = pd.DataFrame(user_playlist_info)
    new_df['date'] = datetime.datetime.now()
    # read the csv file
    old_df = pd.read_csv('user_playlists_info.csv')
    the_index = 0
    previous_index = -1
    for i in range(len(new_df)):
        song_id = new_df['playlist_id'][i]
        try:
            # get the index of the matching value
            index = old_df[old_df['playlist_id'] == song_id].index[0]
            # if the index is not the previous index + 1 and it is not the first index
            if i != previous_index+1 and i != 0:
                # save the index
                the_index = i
            previous_index = i
        except IndexError:
            pass
    changed = new_df[:the_index]

    # replace the rows before the index with the new rows, changed
    old_df[:the_index] = changed
    # save the new dataframe to the csv file
    # old_df.to_csv('user_playlists_info.csv', index=False)
    # return all the playlits that are new
    # store_user_playlists_info() # pause while updating the function
    return changed

# get all the playlists with functions hidden in the name or description
def get_playlists_with_functions():
    new_playlists = get_new_playlists()
    # create a dictonary to store the playlists id with functions
    playlists_with_functions = {}
    # iterate through the new playlists
    for i in range(len(new_playlists)):
        # use gather_functions to check if the playlist name and description has functions
        name = gather_functions(new_playlists['playlist_name'][i].lower())
        description = gather_functions(new_playlists['playlist_description'][i].lower())
        funciton_data = {}
        # print(name)
        # print(description)
        # iterate through the dictonary and check if the value is not None
        for key, value in name.items():
            if value:
                # if both the name and description have different values for the same key set a list with both values
                if description[key] and description[key] != value:
                    funciton_data[key] = [value, description[key]]
                else:
                    funciton_data[key] = [value]
            # add playlist id to the dictonary
            # funciton_data['playlist_id'] = new_playlists['playlist_id'][i]
        # save funciton_data to the playlists_with_functions dictonary with key as the playlist id
        playlists_with_functions[new_playlists['playlist_id'][i]] = funciton_data
    return playlists_with_functions

# search for aritst and return the artist id
def search_for_artist(artist):
    # search for the artist
    results = sp.search(q='artist:' + artist, type='artist')
    artist_id = results['artists']['items'][0]['id']
    return artist_id

# get the all the tracks from the artist
def get_artist_discography(name):
    # Get the artist's albums
    results = sp.artist_albums(search_for_artist(name), album_type='album')
    # Extract relevant data from the API response
    all_tarck_ids = []
    for album in results['items']:

        # Get the tracks of the album
        album_tracks = sp.album_tracks(album['id'])

        # Extract relevant data from the API response
        for idx, track in enumerate(album_tracks['items']):
            print(f"Track {idx+1}: {track['name']} by {track['artists'][0]['name']}")
            print(f"Track ID: {track['id']}")
            all_tarck_ids.append(track['id'])
    return all_tarck_ids

def get_friends_activity_json():
    """ get the friends activity using https://github.com/valeriangalliat/spotify-buddylist repository
    the following code runs the node.js get's the friends activity and converts it to json and returns it"""
    try:
        friends_activity = subprocess.check_output(["node", r"C:\Users\saket\Documents\GitHub\Pyhton\Project Music\spotify api\spotify-buddylist-master\example.js"])
    except subprocess.CalledProcessError as e:
        print(e.output)
        return None
    # decode the bytes to string 
    while True:
        # check if there is a friends_activity.csv file if not create one
        try:
            # read the csv file
            friend_activity_csv = pd.read_csv('friend_activity.csv')
        except FileNotFoundError:
            # create a csv file
            with open('friend_activity.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['user_uri', 'track_uri', 'timestamp', 'current_time'])
        try:
            # read the csv file
            friends_activity_csv = pd.read_csv('friends_activity.csv')
        except FileNotFoundError:
            # create a csv file
            with open('friends_activity.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['user_uri', 'track_uri', 'timestamp', 'current_time'])
        staring_time = datetime.datetime.now()

        # get the friends activity json use a while loop and retry if the request is None
        while True:
            friends_activity_json = get_friends_activity_json()
            if friends_activity_json:
                time.sleep(60) # pause for 1 minute, this is to prevent the api from getting blocked
                break

        # get the current time
        current_time = datetime.datetime.now()
        # iterate through the friends activity

        user_ids = ["gntab9tp1cc5qipthodlvvsm3"]
        user_id = ["spotify:user:"+user_id for user_id in user_ids]
        try:
            for friend in friends_activity_json['friends']:
                
                    # check if the user uri is the same as the user uri
                    if friend['user']['uri'] in user_id:        # only for some selected users
                        track_id = friend['track']['uri'].split(":")[-1]
                        # check if the track is same as the previous track don't add it to the csv file

                        """ This will run if the csv file is empty or if the track is not the same as the previous track"""
                        try:
                            # this means the person is listening to the same song as the previous song
                            if friend['track']['uri'] == friend_activity_csv['track_uri'].iloc[-1]:
                                # print the song name
                                print('listning to the same song',friend['track']['name'])
                                continue
                        except IndexError:
                            pass

                        # write the data to the csv file
                        with open('friend_activity.csv', 'a', newline='') as file:
                            writer = csv.writer(file)
                            print('adding to the database', friend['user']['uri'], friend['track']['uri'], friend['timestamp'], current_time)
                            writer.writerow([friend['user']['uri'], friend['track']['uri'], friend['timestamp'], current_time])

                        '''add the track to the playlist if it is not already in the playlist '''
                        if friend['track']['uri'].split(":")[-1] not in [i['track']['uri'].split(":")[-1] for i in get_playlist_tracks(playlist_id)]:
                            # add the track to the playlist
                            song_id = friend['track']['uri'].split(":")[-1]
                            print(song_id)
                            # print song name
                            print(friend['track']['name'])
                            sp.user_playlist_add_tracks(username, playlist_id, [song_id])
                        else:
                            # move the track to the bottom of the playlist
                            # playlist_modify_private(playlist_id, track_id, len(get_playlist_tracks(playlist_id)))
                            print(len(get_playlist_tracks(playlist_id)))
                            sp.user_playlist_add_tracks(username, playlist_id, [track_id], position=len(get_playlist_tracks(playlist_id)) )

                        """trying to play the track"""
                        # sp.start_playback(uris=[friend['track']['uri']])
                        # add the track to queue
                        # sp.add_to_queue(friend['track']['uri'])
            
            # run this code every 30 minutes using start_time and reset the start_time
            if (datetime.datetime.now() - staring_time).seconds > 1800:
                print('30 hour is over and updating the friends_activity.csv file')
                """ I wan't able to update only if new data is added to the csv file so I am just updating the csv file every 30 minutes"""
                
                # write the data to the csv file
                for friend in friends_activity_json['friends']:
                    with open('friends_activity.csv', 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([friend['user']['uri'], friend['track']['uri'], friend['timestamp'], current_time])
                # reset the staring time
                staring_time = datetime.datetime.now()
            # sleep for 20 seconds
            # print('sleeping for 30 sec')
            for i in range(30):
                print('searching for friends activity in', 30-i, 'sec')
                time.sleep(1)
            # time.sleep(60)
            # break
        except KeyError:
            print('KeyError')
            time.sleep(30)

if __name__ == "__main__":
    store_friends_activity()