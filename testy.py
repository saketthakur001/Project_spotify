
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
# Extracting and inserting data with upsert logic
for table_name, primary_key in primary_keys.items():
    sqlite_cur.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cur.fetchall()
    columns = [desc[0] for desc in sqlite_cur.description]
    columns_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(rows[0])) if rows else ""

    for row in rows:
        # If inserting into the 'streamings' table, check for NULL context_id
        if table_name == "streamings" and row[3] is None:
            # Handle NULL context_id (e.g., skip insertion or replace with a default value)
            continue  # This will skip inserting this particular row
        
        postgres_cur.execute(
            f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT ({primary_key}) DO NOTHING",
            row
        )
    postgres_conn.commit()


# Uncomment the following line to run the function. Ensure the PostgreSQL DB details are correct.
# store_user_data_to_postgresql(friends_activity_json_example)

store_user_data_to_postgresql(main.get_friends_activity_json())
