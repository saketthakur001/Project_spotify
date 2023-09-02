
import main
import psycopg2
import sqlite3

def store_user_data_to_postgresql(friends_activity_json, 
                                  sqlite_db_name='friends_activity.db',
                                  postgres_db_name="FriendsActivity",
                                  user="postgres",
                                  password="whatthe",
                                  host="localhost",
                                  port="5432"):
    postgres_conn = psycopg2.connect(database=postgres_db_name, user=user, password=password, host=host, port=port)
    postgres_cur = postgres_conn.cursor()

    # Creating the tables in PostgreSQL
    tables = [
        '''
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            user_url TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_image_url TEXT
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS albums (
            album_id SERIAL PRIMARY KEY,
            album_uri TEXT NOT NULL,
            album_name TEXT NOT NULL
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS artists (
            artist_id SERIAL PRIMARY KEY,
            artist_uri TEXT NOT NULL,
            artist_name TEXT NOT NULL
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS tracks (
            track_id SERIAL PRIMARY KEY,
            track_uri TEXT NOT NULL,
            track_name TEXT NOT NULL,
            track_image_url TEXT NOT NULL,
            album_id INTEGER NOT NULL REFERENCES albums(album_id),
            artist_id INTEGER NOT NULL REFERENCES artists(artist_id)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS context (
            context_id SERIAL PRIMARY KEY,
            context_uri TEXT NOT NULL,
            context_name TEXT NOT NULL,
            context_index INTEGER NOT NULL
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS streamings (
            user_id INTEGER NOT NULL REFERENCES users(user_id),
            track_id INTEGER NOT NULL REFERENCES tracks(track_id),
            timestamp TEXT NOT NULL,
            context_id INTEGER NOT NULL REFERENCES context(context_id),
            UNIQUE(user_id, track_id, timestamp, context_id)  -- Add this unique constraint
        )
        '''
       
    ]

    for table in tables:
        postgres_cur.execute(table)
    postgres_conn.commit()

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_db_name)
    sqlite_cur = sqlite_conn.cursor()

    # Table primary key mapping for upsert
    primary_keys = {
        "users": "user_id",
        "albums": "album_id",
        "artists": "artist_id",
        "tracks": "track_id",
        "context": "context_id",
        "streamings": "user_id, track_id, timestamp, context_id"  # Corrected composite primary key
    }
    # # Extracting and inserting data with upsert logic
    # for table_name, primary_key in primary_keys.items():
    #     sqlite_cur.execute(f"SELECT * FROM {table_name}")
    #     rows = sqlite_cur.fetchall()
    #     columns = [desc[0] for desc in sqlite_cur.description]
    #     columns_str = ", ".join(columns)
    #     placeholders = ", ".join(["%s"] * len(rows[0])) if rows else ""

    #     for row in rows:
    #         # If inserting into the 'streamings' table, check for NULL context_id
    #         if table_name == "streamings" and row[3] is None:
    #             # Handle NULL context_id (e.g., skip insertion or replace with a default value)
    #             continue  # This will skip inserting this particular row

    #         postgres_cur.execute(
    #             f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT ({primary_key}) DO NOTHING",
    #             row
    #         )
    #     postgres_conn.commit()


# Uncomment the following line to run the function. Ensure the PostgreSQL DB details are correct.
# store_user_data_to_postgresql(friends_activity_json_example)

store_user_data_to_postgresql(True)

def fetch_data_from_postgresql(table_name,
                               postgres_db_name="FriendsActivity",
                               user="postgres",
                               password="whatthe",
                               host="localhost",
                               port="5432"):
    # Connect to PostgreSQL
    postgres_conn = psycopg2.connect(database=postgres_db_name, user=user, password=password, host=host, port=port)
    postgres_cur = postgres_conn.cursor()

    # Fetch data from the specified table
    postgres_cur.execute(f"SELECT * FROM {table_name}")
    records = postgres_cur.fetchall()
    columns = [desc[0] for desc in postgres_cur.description]

    postgres_conn.close()
    return columns, records

print(main.get_friends_activity_json())


def add_friends_data_to_postgresql(friends_data, 
                                  postgres_db_name="FriendsActivity",
                                  user="postgres",
                                  password="whatthe",
                                  host="localhost",
                                  port="5432"):
    # Connect to PostgreSQL
    postgres_conn = psycopg2.connect(database=postgres_db_name, user=user, password=password, host=host, port=port)
    postgres_cur = postgres_conn.cursor()

    for data in friends_data:
        # User data extraction and insertion
        user_uri = data['user']['uri']
        user_name = data['user']['name']
        user_image = data['user']['imageUrl']

        postgres_cur.execute(
            "INSERT INTO users (user_url, user_name, user_image_url) VALUES (%s, %s, %s) ON CONFLICT (user_url) DO NOTHING",
            (user_uri, user_name, user_image)
        )

        # Album data extraction and insertion
        album_uri = data['track']['album']['uri']
        album_name = data['track']['album']['name']

        postgres_cur.execute(
            "INSERT INTO albums (album_uri, album_name) VALUES (%s, %s) ON CONFLICT (album_uri) DO NOTHING",
            (album_uri, album_name)
        )

        # Artist data extraction and insertion
        artist_uri = data['track']['artist']['uri']
        artist_name = data['track']['artist']['name']

        postgres_cur.execute(
            "INSERT INTO artists (artist_uri, artist_name) VALUES (%s, %s) ON CONFLICT (artist_uri) DO NOTHING",
            (artist_uri, artist_name)
        )

        # Track data extraction and insertion
        track_uri = data['track']['uri']
        track_name = data['track']['name']
        track_image = data['track']['imageUrl']

        postgres_cur.execute(
            """INSERT INTO tracks (track_uri, track_name, track_image_url, album_id, artist_id) 
               VALUES (%s, %s, %s, 
                       (SELECT album_id FROM albums WHERE album_uri = %s), 
                       (SELECT artist_id FROM artists WHERE artist_uri = %s)) 
               ON CONFLICT (track_uri) DO NOTHING""",
            (track_uri, track_name, track_image, album_uri, artist_uri)
        )

        # Context data extraction and insertion
        context_uri = data['track']['context']['uri']
        context_name = data['track']['context']['name']
        context_index = data['track']['context']['index']

        postgres_cur.execute(
            "INSERT INTO context (context_uri, context_name, context_index) VALUES (%s, %s, %s) ON CONFLICT (context_uri) DO NOTHING",
            (context_uri, context_name, context_index)
        )

        # Streamings data extraction and insertion
        timestamp = data['timestamp']

        postgres_cur.execute(
            """INSERT INTO streamings (user_id, track_id, timestamp, context_id) 
               VALUES (
                   (SELECT user_id FROM users WHERE user_url = %s), 
                   (SELECT track_id FROM tracks WHERE track_uri = %s), 
                   %s, 
                   (SELECT context_id FROM context WHERE context_uri = %s)
               ) 
               ON CONFLICT (user_id, track_id, timestamp, context_id) DO NOTHING""",
            (user_uri, track_uri, timestamp, context_uri)
        )

    postgres_conn.commit()
    postgres_conn.close()

# Example friends data
# friends_data = [
#     {
#         'timestamp': 1690609572062, 
#         'user': {'uri': 'spotify:user:homestar99', 'name': 'Eliott', 'imageUrl': 'https://i.scdn.co/image/ab67757000003b82c53693eae40a7069725a0785'}, 
#         'track': {
#             'uri': 'spotify:track:3deWxhcgA9D5ww7YcPQltQ', 
#             'name': 'Dinner for Two', 
#             'imageUrl': 'http://i.scdn.co/image/ab67616d0000b273258152311d36cc59f779c3a7', 
#             'album': {'uri': 'spotify:album:4oRaFi044yhwH77gUXbH5I', 'name': 'Love This Giant'}, 
#             'artist': {'uri': 'spotify:artist:20vuBdFblWUo2FCOvUzusB', 'name': 'David Byrne'}, 
#             'context': {'uri': 'spotify:playlist:4RSutFssm5BrHALNngF9hf', 'name': "That's Why God Made the Radio", 'index': 0}
#         }
#     }, 
#     {
#         'timestamp': 1690726442406, 
#         'user': {'uri': 'spotify:user:sonemic.com', 'name': 'sonemic.com', 'imageUrl': 'https://i.scdn.co/image/ab67757000003b82642ce4dbd1cab92bc267868f'}, 
#         'track': {
#             'uri': 'spotify:track:7z3OJLElVcKcNty1TIjCUD', 
#             'name': 'Vulture City', 
#             'imageUrl': 'http://i.scdn.co/image/ab67616d0000b273046b6e3667aaf93d653a4adf', 
#             'album': {'uri': 'spotify:album:3UkxfZIq4pYDTNB7XCPDdm', 'name': 'Arizona EP'}, 
#             'artist': {'uri': 'spotify:artist:13xKCVJaX32BL7EN9IOiCM', 'name': 'venturing'}, 
#             'context': {'uri': 'spotify:playlist:5W94VfaMlhjtZaRhidGD20', 'name': '2023 | Sonemic Selects', 'index': 0}
#         }
#     }
# ]

# Uncomment to run the function with the example data
# add_friends_data_to_postgresql(friends_data)


# Example usage
# table_data = fetch_data_from_postgresql("artists")
# print(table_data)

