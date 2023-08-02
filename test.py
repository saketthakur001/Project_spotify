from spotify_manager import *
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
# playlist_modify_public = get_spotify_token("playlist-modify-public")

# user-read-recently-played
# user_read_recently_played = get_spotify_token("user-read-recently-played")
user_read_recently_played = spotipy.util.prompt_for_user_token(username, scope="user-read-recently-played")

# user-top-read
# user_top_read = get_spotify_token("user-top-read")

# playlist-modify-private
# playlist_modify_private = get_spotify_token("playlist-modify-private")

# user-library-read
# user_library_read = get_spotify_token("user-library-read")

# playlist-read-private
# playlist_read_private = get_spotify_token("playlist-read-private")

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
# def get_playlist_tracks_retry(playlist_id):
#     """retry 3 times to get the playlist tracks

#     Parameters
#     ----------
#     playlist_id : str

#     Returns
#     -------
#     results : dict
#     """
#     for i in range(9999**9999):
#         try:
#             results = get_playlist_tracks(playlist_id)
#             return results
#         except Exception as e:
#             print(f"Error fetching playlist tracks: {e}")
#             print(f"Retrying in 10 seconds ({i+1}/20 attempts)...")
#             if i < 3:
#                 time.sleep(10)
#                 print('sleeping for 10 seconds')
#             elif i < 5:
#                 time.sleep(30)
#                 print('sleeping for 30 seconds')
#             else:
#                 time.sleep(60)
#                 print('sleeping for 60 seconds')
#     return None


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

# def get_recently_played_tracks(limit=50):
#     """ Get the recently played tracks from the user's account.

#     parameters
#     ----------
#     limit : int (default=50)
#         The number of tracks to return. Default: 50. Minimum: 1. Maximum: 50.
    
#     Returns
#     -------
#     recently_played : dict
#         A dictionary containing the recently played tracks and their listening time.
#         The keys are 'tracks' and 'listening_time'.
#     """
#     recently_played = user_read_recently_played.current_user_recently_played(limit=limit, )
#     listening_time = sum([track['duration_ms'] for track in recently_played['items']])
#     return {'tracks': recently_played, 'listening_time': listening_time}

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

def parse_my_streaming_history():

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
    sorted_playlist = []
    for i in range(len(user_playlist_tracks['items'])):
        track = user_playlist_tracks['items'][i]['track']
        popularity = track['popularity']
        sorted_playlist.append(popularity)
    sorted_playlist.sort(reverse=True)
    return sorted_playlist


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


r = get_recently_played()

print(r)