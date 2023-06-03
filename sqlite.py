
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

    # # create a table for streamings with columns for user_id, track_id and timestamp
    # # add foreign key constraints to reference the user_id and track_id from the users and tracks tables respectively
    # cur.execute('''CREATE TABLE IF NOT EXISTS streamings(
    #     user_id INTEGER NOT NULL,
    #     track_id INTEGER NOT NULL,
    #     timestamp TEXT NOT NULL,
    #     FOREIGN KEY (user_id) REFERENCES users(user_id),
    #     FOREIGN KEY (track_id) REFERENCES tracks(track_id)
    # )
    # ''')

     # create a table for streamings with columns for user_id, track_id, timestamp and context_id
    # add foreign key constraints to reference the user_id, track_id and context_id from the users, tracks and context tables respectively
    cur.execute('''CREATE TABLE IF NOT EXISTS streamings(
        user_id INTEGER NOT NULL,
        track_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        context_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (track_id) REFERENCES tracks(track_id),
        FOREIGN KEY (context_id) REFERENCES context(context_id)
    )
    ''')


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

        # # check if there is already a streaming with the same timestamp in the streamings table by querying the timestamp column
        # cur.execute("SELECT * FROM streamings WHERE timestamp = ?", (timestamp,))
        # streaming = cur.fetchone()

        # # if the query returns None, it means there is no streaming with the same timestamp in the table
        # if streaming is None:
        #     # insert a new row into the streamings table with the user_id, track_id and timestamp values
        #     cur.execute("INSERT INTO streamings (user_id, track_id, timestamp) VALUES (?, ?, ?)", (user_id, track_id, timestamp))
        #     conn.commit()

        # check if there is already a streaming with the same timestamp in the streamings table by querying the timestamp column
        cur.execute("SELECT * FROM streamings WHERE timestamp = ?", (timestamp,))
        streaming = cur.fetchone()

        # if the query returns None, it means there is no streaming with the same timestamp in the table
        if streaming is None:
            # insert a new row into the streamings table with the user_id, track_id, timestamp and context_id values
            cur.execute("INSERT INTO streamings (user_id, track_id, timestamp, context_id) VALUES (?, ?, ?, ?)", (user_id, track_id, timestamp, context_id))
            conn.commit()

# define a class for friends activity analysis
class FriendActivityAnaliser:
    # define the constructor method that takes the database name as an input
    def __init__(self, database_name="friends_activity.db"):
        # store the database name as an attribute
        self.database_name = database_name
        # try to connect to the database and create a cursor object
        try:
            self.conn = sqlite3.connect(self.database_name)
            self.cur = self.conn.cursor()
            print(f"Connected to {self.database_name} successfully.")
        except sqlite3.Error as e:
            print(f"Error connecting to {self.database_name}: {e}")

    # define a method that returns the most played tracks for a given user or users, time period, artist or artists, album or albums and limit
    def top_tracks(self, user_id=None, time_period=None, by_artist_uri=None, by_album_uri=None, limit=None):
        # construct the SQL query to select the user name, track uri, track name, artist uri, album uri, album name and count the number of streamings for each track
        sql = """SELECT u.user_name, t.track_uri, t.track_name, a.artist_uri, al.album_uri, al.album_name, COUNT(s.track_id) AS streamings
                 FROM users u
                 JOIN streamings s ON u.user_id = s.user_id -- join the users and streamings tables on user_id
                 JOIN tracks t ON s.track_id = t.track_id -- join the streamings and tracks tables on track_id
                 JOIN artists a ON t.artist_id = a.artist_id -- join the tracks and artists tables on artist_id
                 JOIN albums al ON t.album_id = al.album_id -- join the tracks and albums tables on album_id
                 """

        # initialize a list to store the query parameters
        params = []

        # if user_id is not None, add a WHERE clause to filter by user_id
        if user_id is not None:
            # if user_id is a single value, use the equal operator
            if isinstance(user_id, int):
                sql += " WHERE u.user_id = ?"
                params.append(user_id)
            # if user_id is a list or tuple of values, use the IN operator
            elif isinstance(user_id, (list, tuple)):
                sql += f" WHERE u.user_id IN ({','.join(['?'] * len(user_id))})"
                params.extend(user_id)

        # if time_period is not None, add a AND clause to filter by timestamp
        if time_period is not None:
            # if time_period is a tuple of start and end values, use the BETWEEN operator
            if isinstance(time_period, tuple) and len(time_period) == 2:
                sql += " AND s.timestamp BETWEEN ? AND ?"
                params.extend(time_period)
            # if time_period is a single value for start or end, use the greater than or equal or less than or equal operator
            elif isinstance(time_period, str):
                # check if the value starts with '>' or '<' and use the corresponding operator
                if time_period.startswith('>'):
                    sql += " AND s.timestamp >= ?"
                    params.append(time_period[1:])
                elif time_period.startswith('<'):
                    sql += " AND s.timestamp <= ?"
                    params.append(time_period[1:])

        # if by_artist_uri is not None, add a AND clause to filter by artist_uri
        if by_artist_uri is not None:
            # if by_artist_uri is a single value, use the equal operator
            if isinstance(by_artist_uri, str):
                sql += " AND a.artist_uri = ?"
                params.append(by_artist_uri)
            # if by_artist_uri is a list or tuple of values, use the IN operator
            elif isinstance(by_artist_uri, (list, tuple)):
                sql += f" AND a.artist_uri IN ({','.join(['?'] * len(by_artist_uri))})"
                params.extend(by_artist_uri)

        # if by_album_uri is not None, add a AND clause to filter by album_uri
        if by_album_uri is not None:
            # if by_album_uri is a single value, use the equal operator
            if isinstance(by_album_uri, str):
                sql += " AND al.album_uri = ?"
                params.append(by_album_uri)
            # if by_album_uri is a list or tuple of values, use the IN operator
            elif isinstance(by_album_uri, (list, tuple)):
                sql += f" AND al.album_uri IN ({','.join(['?'] * len(by_album_uri))})"
                params.extend(by_album_uri)

        # group by user name, track uri, track name, artist uri, album uri and album name
        sql += " GROUP BY u.user_name, t.track_uri, t.track_name, a.artist_uri , al.album_uri , al.album_name"

        # order by streamings in descending order
        sql += " ORDER BY streamings DESC"

        # if limit is not None and is an integer value greater than zero, add a LIMIT clause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
    # define a method that returns the most played artists for a given user or users, time period, and limit
    def top_artists(self, user_id=None, time_period=None, limit=None):
        # construct the SQL query to select the user name, artist uri, artist name, and count the number of streamings for each artist
        sql = """SELECT u.user_name, a.artist_uri, a.artist_name, COUNT(s.track_id) AS streamings
                FROM users u
                JOIN streamings s ON u.user_id = s.user_id -- join the users and streamings tables on user_id
                JOIN tracks t ON s.track_id = t.track_id -- join the streamings and tracks tables on track_id
                JOIN artists a ON t.artist_id = a.artist_id -- join the tracks and artists tables on artist_id
                """

        # initialize a list to store the query parameters
        params = []

        # if user_id is not None, add a WHERE clause to filter by user_id
        if user_id is not None:
            # if user_id is a single value, use the equal operator
            if isinstance(user_id, int):
                sql += " WHERE u.user_id = ?"
                params.append(user_id)
            # if user_id is a list or tuple of values, use the IN operator
            elif isinstance(user_id, (list, tuple)):
                sql += f" WHERE u.user_id IN ({','.join(['?'] * len(user_id))})"
                params.extend(user_id)

        # if time_period is not None, add an AND clause to filter by timestamp
        if time_period is not None:
            # if time_period is a tuple of start and end values, use the BETWEEN operator
            if isinstance(time_period, tuple) and len(time_period) == 2:
                sql += " AND s.timestamp BETWEEN ? AND ?"
                params.extend(time_period)
            # if time_period is a single value for start or end, use the greater than or equal or less than or equal operator
            elif isinstance(time_period, str):
                # check if the value starts with '>' or '<' and use the corresponding operator
                if time_period.startswith('>'):
                    sql += " AND s.timestamp >= ?"
                    params.append(time_period[1:])
                elif time_period.startswith('<'):
                    sql += " AND s.timestamp <= ?"
                    params.append(time_period[1:])

        # group by user name, artist uri, and artist name
        sql += " GROUP BY u.user_name, a.artist_uri, a.artist_name"

        # order by streamings in descending order
        sql += " ORDER BY streamings DESC"

        # if limit is not None and is an integer value greater than zero, add a LIMIT clause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

    
    # define a function that returns the users that listened to a particular artist the most
    def top_users_by_artist(self, artist_id, limit=None):
        # construct the SQL query that joins the users, streamings, tracks, and artists tables on their respective columns and filters by the given artist_id
        sql = """SELECT u.user_name, u.user_image_url, COUNT(s.track_id) AS streamings
                FROM users u
                JOIN streamings s ON u.user_id = s.user_id
                JOIN tracks t ON s.track_id = t.track_id
                JOIN artists a ON t.artist_id = a.artist_id
                WHERE a.artist_id = ?
                GROUP BY u.user_name, u.user_image_url
                ORDER BY streamings DESC
            """

        # initialize a list to store the query parameters
        params = []

        # add the artist_id parameter to the list
        params.append(artist_id)

        # if limit is not None and is an integer value greater than zero, add a LIMIT clause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

    # define a method that returns the most played albums for a given user or users, time period, and limit
    def top_albums(self, user_id=None, time_period=None, limit=None):
        # construct the SQL query to select the user name, album uri, album name, and count the number of streamings for each album
        sql = """SELECT u.user_name, al.album_uri, al.album_name, COUNT(s.track_id) AS streamings
                FROM users u
                JOIN streamings s ON u.user_id = s.user_id -- join the users and streamings tables on user_id
                JOIN tracks t ON s.track_id = t.track_id -- join the streamings and tracks tables on track_id
                JOIN albums al ON t.album_id = al.album_id -- join the tracks and albums tables on album id
                """

        # initialize a list to store the query parameters
        params = []

        # if user_id is not None, add a WHERE clause to filter by user_id
        if user_id is not None:
            # if user_id is a single value, use the equal operator
            if isinstance(user_id, int):
                sql += " WHERE u.user_id = ?"
                params.append(user_id)
            # if user_id is a list or tuple of values, use the IN operator
            elif isinstance(user_id, (list, tuple)):
                sql += f" WHERE u.user_id IN ({','.join(['?'] * len(user_id))})"
                params.extend(user_id)

        # if time_period is not None, add an AND clause to filter by timestamp
        if time_period is not None:
            # if time_period is a tuple of start and end values, use the BETWEEN operator
            if isinstance(time_period, tuple) and len(time_period) == 2:
                sql += " AND s.timestamp BETWEEN ? AND ?"
                params.extend(time_period)
            # if time_period is a single value for start or end, use the greater than or equal or less than or equal operator
            elif isinstance(time_period, str):
                # check if the value starts with '>' or '<' and use the corresponding operator
                if time_period.startswith('>'):
                    sql += " AND s.timestamp >= ?"
                    params.append(time_period[1:])
                elif time_period.startswith('<'):
                    sql += " AND s.timestamp <= ?"
                    params.append(time_period[1:])

        # group by user name, album uri, and album name
        sql += " GROUP BY u.user_name, al.album_uri, al.album_name"

        # order by streamings in descending order
        sql += " ORDER BY streamings DESC"

        # if limit is not None and is an integer value greater than zero, add a LIMIT clause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

    # define a method that returns the most played artists for a given user or users, time period, and limit
    def top_contexts(self, user_id=None, time_period=None, limit=None, most_played_songs_in_the_context=1):
        # construct the SQL query to select the user name, context URI, context name, count the number of streamings for each context, and the most played song or songs in the context
        sql = """SELECT u.user_name, c.context_uri, c.context_name, COUNT(s.track_id) AS streamings,
                (SELECT t.track_name || ' (' || COUNT(s2.track_id) || ')' -- concatenate the track name and the number of streamings for each track in the context
                FROM streamings s2
                JOIN tracks t ON s2.track_id = t.track_id -- join the streamings and tracks tables on track_id
                WHERE s2.context_id = s.context_id -- filter by the same context_id as in the outer query
                GROUP BY t.track_name, t.track_id -- group by track name and track id
                ORDER BY COUNT(s2.track_id) DESC -- order by streamings in descending order
                LIMIT ? -- limit by the most_played_songs_in_the_context parameter
                ) AS most_played_songs_in_the_context
                FROM users u
                JOIN streamings s ON u.user_id = s.user_id -- join the users and streamings tables on user_id
                JOIN context c ON s.context_id = c.context_id -- join the streamings and context tables on context_id
            """

        # initialize a list to store the query parameters
        params = []

        # add the most_played_songs_in_the_context parameter to the list
        params.append(most_played_songs_in_the_context)

        # if user_id is not None, add a WHERE clause to filter by user_id
        if user_id is not None:
            # if user_id is a single value, use the equal operator
            if isinstance(user_id, int):
                sql += " WHERE u.user_id = ?"
                params.append(user_id)
            # if user_id is a list or tuple of values, use the IN operator
            elif isinstance(user_id, (list, tuple)):
                sql += f" WHERE u.user_id IN ({','.join(['?'] * len(user_id))})"
                params.extend(user_id)

        # if time_period is not None, add an AND clause to filter by timestamp
        if time_period is not None:
            # if time_period is a tuple of start and end values, use the BETWEEN operator
            if isinstance(time_period, tuple) and len(time_period) == 2:
                sql += " AND s.timestamp BETWEEN ? AND ?"
                params.extend(time_period)
            # if time_period is a single value for start or end, use the greater than or equal or less than or equal operator
            elif isinstance(time_period, str):
                # check if the value starts with '>' or '<' and use the corresponding operator
                if time_period.startswith('>'):
                    sql += " AND s.timestamp >= ?"
                    params.append(time_period[1:])
                elif time_period.startswith('<'):
                    sql += " AND s.timestamp <= ?"
                    params.append(time_period[1:])

        # group by user name, context URI, and context name
        sql += " GROUP BY u.user_name, c.context_uri, c.context_name"

        # order by streamings in descending order
        sql += " ORDER BY streamings DESC"

        # if limit is not None and is an integer value greater than zero, add a LIMIT clause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")# define a class for friends activity analysis

class FriendActivityAnaliser:
    # define the constructor method that takes the database name as an input
    def __init__(self, database_name="friends_activity.db"):
        # store the database name as an attribute
        self.database_name = database_name
        # try to connect to the database and create a cursor object
        try:
            self.conn = sqlite3.connect(self.database_name)
            self.cur = self.conn.cursor()
            print(f"Connected to {self.database_name} successfully.")
        except sqlite3.Error as e:
            print(f"Error connecting to {self.database_name}: {e}")

    # define a method that returns the most played tracks for a given user or users, time period, artist or artists, album or albums and limit
    def top_tracks(self, user_id=None, time_period=None, by_artist_uri=None, by_album_uri=None, limit=None):
        # construct the SQL query to select the user name, track uri, track name, artist uri, album uri, album name and count the number of streamings for each track
        sql = """SELECT u.user_name, t.track_uri, t.track_name, a.artist_uri, al.album_uri, al.album_name, COUNT(s.track_id) AS streamings
                 FROM users u
                 JOIN streamings s ON u.user_id = s.user_id -- join the users and streamings tables on user_id
                 JOIN tracks t ON s.track_id = t.track_id -- join the streamings and tracks tables on track_id
                 JOIN artists a ON t.artist_id = a.artist_id -- join the tracks and artists tables on artist_id
                 JOIN albums al ON t.album_id = al.album_id -- join the tracks and albums tables on album_id
                 """

        # initialize a list to store the query parameters
        params = []

        # if user_id is not None, add a WHERE clause to filter by user_id
        if user_id is not None:
            # if user_id is a single value, use the equal operator
            if isinstance(user_id, int):
                sql += " WHERE u.user_id = ?"
                params.append(user_id)
            # if user_id is a list or tuple of values, use the IN operator
            elif isinstance(user_id, (list, tuple)):
                sql += f" WHERE u.user_id IN ({','.join(['?'] * len(user_id))})"
                params.extend(user_id)

        # if time_period is not None, add a AND clause to filter by timestamp
        if time_period is not None:
            # if time_period is a tuple of start and end values, use the BETWEEN operator
            if isinstance(time_period, tuple) and len(time_period) == 2:
                sql += " AND s.timestamp BETWEEN ? AND ?"
                params.extend(time_period)
            # if time_period is a single value for start or end, use the greater than or equal or less than or equal operator
            elif isinstance(time_period, str):
                # check if the value starts with '>' or '<' and use the corresponding operator
                if time_period.startswith('>'):
                    sql += " AND s.timestamp >= ?"
                    params.append(time_period[1:])
                elif time_period.startswith('<'):
                    sql += " AND s.timestamp <= ?"
                    params.append(time_period[1:])

        # if by_artist_uri is not None, add a AND clause to filter by artist_uri
        if by_artist_uri is not None:
            # if by_artist_uri is a single value, use the equal operator
            if isinstance(by_artist_uri, str):
                sql += " AND a.artist_uri = ?"
                params.append(by_artist_uri)
            # if by_artist_uri is a list or tuple of values, use the IN operator
            elif isinstance(by_artist_uri, (list, tuple)):
                sql += f" AND a.artist_uri IN ({','.join(['?'] * len(by_artist_uri))})"
                params.extend(by_artist_uri)

        # if by_album_uri is not None, add a AND clause to filter by album_uri
        if by_album_uri is not None:
            # if by_album_uri is a single value, use the equal operator
            if isinstance(by_album_uri, str):
                sql += " AND al.album_uri = ?"
                params.append(by_album_uri)
            # if by_album_uri is a list or tuple of values, use the IN operator
            elif isinstance(by_album_uri, (list, tuple)):
                sql += f" AND al.album_uri IN ({','.join(['?'] * len(by_album_uri))})"
                params.extend(by_album_uri)

        # group by user name, track uri, track name, artist uri, album uri and album name
        sql += " GROUP BY u.user_name, t.track_uri, t.track_name, a.artist_uri , al.album_uri , al.album_name"

        # order by streamings in descending order
        sql += " ORDER BY streamings DESC"

        # if limit is not None and is an integer value greater than zero, add a LIMIT clause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
    # define a method that returns the most played artists for a given user or users, time period, and limit
    def top_artists(self, user_id=None, time_period=None, limit=None):
        # construct the SQL query to select the user name, artist uri, artist name, and count the number of streamings for each artist
        sql = """SELECT u.user_name, a.artist_uri, a.artist_name, COUNT(s.track_id) AS streamings
                FROM users u
                JOIN streamings s ON u.user_id = s.user_id -- join the users and streamings tables on user_id
                JOIN tracks t ON s.track_id = t.track_id -- join the streamings and tracks tables on track_id
                JOIN artists a ON t.artist_id = a.artist_id -- join the tracks and artists tables on artist_id
                """

        # initialize a list to store the query parameters
        params = []

        # if user_id is not None, add a WHERE clause to filter by user_id
        if user_id is not None:
            # if user_id is a single value, use the equal operator
            if isinstance(user_id, int):
                sql += " WHERE u.user_id = ?"
                params.append(user_id)
            # if user_id is a list or tuple of values, use the IN operator
            elif isinstance(user_id, (list, tuple)):
                sql += f" WHERE u.user_id IN ({','.join(['?'] * len(user_id))})"
                params.extend(user_id)

        # if time_period is not None, add an AND clause to filter by timestamp
        if time_period is not None:
            # if time_period is a tuple of start and end values, use the BETWEEN operator
            if isinstance(time_period, tuple) and len(time_period) == 2:
                sql += " AND s.timestamp BETWEEN ? AND ?"
                params.extend(time_period)
            # if time_period is a single value for start or end, use the greater than or equal or less than or equal operator
            elif isinstance(time_period, str):
                # check if the value starts with '>' or '<' and use the corresponding operator
                if time_period.startswith('>'):
                    sql += " AND s.timestamp >= ?"
                    params.append(time_period[1:])
                elif time_period.startswith('<'):
                    sql += " AND s.timestamp <= ?"
                    params.append(time_period[1:])

        # group by user name, artist uri, and artist name
        sql += " GROUP BY u.user_name, a.artist_uri, a.artist_name"

        # order by streamings in descending order
        sql += " ORDER BY streamings DESC"

        # if limit is not None and is an integer value greater than zero, add a LIMIT clause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
    
    # define a function that returns the users that listened to a particular artist the most
    def top_users_by_artist(self, artist_id, limit=None):
        # construct the SQL query that joins the users, streamings, tracks, and artists tables on their respective columns and filters by the given artist_id
        sql = """SELECT u.user_name, u.user_image_url, COUNT(s.track_id) AS streamings
                FROM users u
                JOIN streamings s ON u.user_id = s.user_id
                JOIN tracks t ON s.track_id = t.track_id
                JOIN artists a ON t.artist_id = a.artist_id
                WHERE a.artist_id = ?
                GROUP BY u.user_name, u.user_image_url
                ORDER BY streamings DESC
            """

        # initialize a list to store the query parameters
        params = []

        # add the artist_id parameter to the list
        params.append(artist_id)

        # if limit is not None and is an integer value greater than zero, add a LIMIT clause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

    # define a method that returns the most played albums for a given user or users, time period, and limit
    def top_albums(self, user_id=None, time_period=None, limit=None):
        # construct the SQL query to select the user name, album uri, album name, and count the number of streamings for each album
        sql = """SELECT u.user_name, al.album_uri, al.album_name, COUNT(s.track_id) AS streamings
                FROM users u
                JOIN streamings s ON u.user_id = s.user_id -- join the users and streamings tables on user_id
                JOIN tracks t ON s.track_id = t.track_id -- join the streamings and tracks tables on track_id
                JOIN albums al ON t.album_id = al.album_id -- join the tracks and albums tables on album id
                """

        # initialize a list to store the query parameters
        params = []

        # if user_id is not None, add a WHERE clause to filter by user_id
        if user_id is not None:
            # if user_id is a single value, use the equal operator
            if isinstance(user_id, int):
                sql += " WHERE u.user_id = ?"
                params.append(user_id)
            # if user_id is a list or tuple of values, use the IN operator
            elif isinstance(user_id, (list, tuple)):
                sql += f" WHERE u.user_id IN ({','.join(['?'] * len(user_id))})"
                params.extend(user_id)

        # if time_period is not None, add an AND clause to filter by timestamp
        if time_period is not None:
            # if time_period is a tuple of start and end values, use the BETWEEN operator
            if isinstance(time_period, tuple) and len(time_period) == 2:
                sql += " AND s.timestamp BETWEEN ? AND ?"
                params.extend(time_period)
            # if time_period is a single value for start or end, use the greater than or equal or less than or equal operator
            elif isinstance(time_period, str):
                # check if the value starts with '>' or '<' and use the corresponding operator
                if time_period.startswith('>'):
                    sql += " AND s.timestamp >= ?"
                    params.append(time_period[1:])
                elif time_period.startswith('<'):
                    sql += " AND s.timestamp <= ?"
                    params.append(time_period[1:])

        # group by user name, album uri, and album name
        sql += " GROUP BY u.user_name, al.album_uri, al.album_name"

        # order by streamings in descending order
        sql += " ORDER BY streamings DESC"

        # if limit is not None and is an integer value greater than zero, add a LIMIT clause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

    # define a method that returns the most played artists for a given user or users, time period, and limit
    def top_contexts(self, user_id=None, time_period=None, limit=None, most_played_songs_in_the_context=1):
        # construct the SQL query to select the user name, context URI, context name, count the number of streamings for each context, and the most played song or songs in the context
        sql = """SELECT u.user_name, c.context_uri, c.context_name, COUNT(s.track_id) AS streamings,
                (SELECT t.track_name || ' (' || COUNT(s2.track_id) || ')' -- concatenate the track name and the number of streamings for each track in the context
                FROM streamings s2
                JOIN tracks t ON s2.track_id = t.track_id -- join the streamings and tracks tables on track_id
                WHERE s2.context_id = s.context_id -- filter by the same context_id as in the outer query
                GROUP BY t.track_name, t.track_id -- group by track name and track id
                ORDER BY COUNT(s2.track_id) DESC -- order by streamings in descending order
                LIMIT ? -- limit by the most_played_songs_in_the_context parameter
                ) AS most_played_songs_in_the_context
                FROM users u
                JOIN streamings s ON u.user_id = s.user_id -- join the users and streamings tables on user_id
                JOIN context c ON s.context_id = c.context_id -- join the streamings and context tables on context_id
            """

        # initialize a list to store the query parameters
        params = []

        # add the most_played_songs_in_the_context parameter to the list
        params.append(most_played_songs_in_the_context)

        # if user_id is not None, add a WHERE clause to filter by user_id
        if user_id is not None:
            # if user_id is a single value, use the equal operator
            if isinstance(user_id, int):
                sql += " WHERE u.user_id = ?"
                params.append(user_id)
            # if user_id is a list or tuple of values, use the IN operator
            elif isinstance(user_id, (list, tuple)):
                sql += f" WHERE u.user_id IN ({','.join(['?'] * len(user_id))})"
                params.extend(user_id)

        # if time_period is not None, add an AND clause to filter by timestamp
        if time_period is not None:
            # if time_period is a tuple of start and end values, use the BETWEEN operator
            if isinstance(time_period, tuple) and len(time_period) == 2:
                sql += " AND s.timestamp BETWEEN ? AND ?"
                params.extend(time_period)
            # if time_period is a single value for start or end, use the greater than or equal or less than or equal operator
            elif isinstance(time_period, str):
                # check if the value starts with '>' or '<' and use the corresponding operator
                if time_period.startswith('>'):
                    sql += " AND s.timestamp >= ?"
                    params.append(time_period[1:])
                elif time_period.startswith('<'):
                    sql += " AND s.timestamp <= ?"
                    params.append(time_period[1:])

        # group by user name, context URI, and context name
        sql += " GROUP BY u.user_name, c.context_uri, c.context_name"

        # order by streamings in descending order
        sql += " ORDER BY streamings DESC"

        # if limit is not None and is an integer value greater than zero, add a LIMIT calause to limit the result to the given limit value
        if limit is not None and isinstance(limit, int) and limit > 0:
            sql += f" LIMIT {limit}"

        # try to execute the query and fetch the results
        try:
            self.cur.execute(sql, params)
            results = self.cur.fetchall()
            # return the results as a list of tuples
            return results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")


import time
import colorama
from colorama import Fore, Style

def count_down(time_in_sec, text):
    '''
    This function takes a time in seconds and a text as arguments and prints a countdown
    '''
    # initialize colorama
    colorama.init()
    
    # loop through the time in seconds
    for i in range(time_in_sec, 0, -1):
        # try to print the text with the time in seconds in green color
        try:
            print(Fore.GREEN + text.format(time=i) + Style.RESET_ALL, end="\r", flush=True)
            # print(Fore.GREEN + "Time left: " + Fore.RED + "{time}".format(time=i) + Style.RESET_ALL + " seconds", end="\r", flush=True)
            # print(Fore.GREEN + "Time left: " + Fore.RED + "{time}".format(time=i) + Fore.GREEN + " seconds" + Style.RESET_ALL, end="\r", flush=True)

            # wait one second
            time.sleep(1)
        # except keyboard interrupt error and print a message in red color
        except KeyboardInterrupt:
            print(Fore.RED + "\nCountdown interrupted by user." + Style.RESET_ALL)
            break
    
    # print a final message in yellow color
    print(Fore.YELLOW + "\nCountdown finished." + Style.RESET_ALL)

count_down(10, "Time left: {time} seconds")