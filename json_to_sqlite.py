''' didn't work because of circular import, I thought who clare just add it to main file'''
import sqlite3
import main

# define a function to store the user data to a database
def store_user_data_to_database(friends_activity_json = main.get_friends_activity_json(), database_name='friends_activity.db'):
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
        user_url TEXT NOT NULL,
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
        print(data)
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

    #select all the data from the users table
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    #print the user data
    print("Users:")
    for user in users:
        print(user)

    #select all the data from the albums table
    cur.execute("SELECT * FROM albums")
    albums = cur.fetchall()

    #print the album data
    print("Albums:")
    for album in albums:
        print(album)

    #select all the data from the artists table
    cur.execute("SELECT * FROM artists")
    artists = cur.fetchall()

    #print the artist data
    print("Artists:")
    for artist in artists:
        print(artist)

    #select all the data from the tracks table
    cur.execute("SELECT * FROM tracks")
    tracks = cur.fetchall()

    #print the track data
    print("Tracks:")
    for track in tracks:
        print(track)

    #select all the data from the context table
    cur.execute("SELECT * FROM context")
    context = cur.fetchall()

    #print the context data
    print("Context:")
    for c in context:
        print(c)

    #select all the data from the streamings table
    cur.execute("SELECT * FROM streamings")
    streamings = cur.fetchall()

    #print the streaming data
    print("Streamings:")
    for streaming in streamings:
        print(streaming)



if __name__ == "__main__":

    #get the data from the JSON file
    # friends_activity_json = get_friends_activity_json()

    #store the data from the JSON file to the database
    store_user_data_to_database()