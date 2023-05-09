from datetime import datetime
import time
import sqlite3
import main
import json

# milliseconds to datetime
def milliseconds_to_datetime(milliseconds):
    return datetime.fromtimestamp(milliseconds / 1000.0)

# get the friends activity json object from the main.py
friends_activity_json = main.get_friends_activity_json()

current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# Use a context manager to connect to the SQLite database.
with sqlite3.connect('friends_activity.sqlite') as conn:
#
    # Connect to the SQLite database.
    cur = conn.cursor()
    # create the users table with user_id as the primary key
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_uri TEXT NOT NULL UNIQUE,
            user_name TEXT NOT NULL,
            user_imageUrl TEXT NOT NULL
        )
    ''')

    # create the tracks table with track_id as the primary key
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            track_id INTEGER PRIMARY KEY,
            track_uri TEXT NOT NULL UNIQUE,
            track_name TEXT NOT NULL,
            track_imageUrl TEXT NOT NULL,
            track_album_uri TEXT NOT NULL,
            track_album_name TEXT NOT NULL,
            track_artist_uri TEXT NOT NULL,
            track_artist_name TEXT NOT NULL
        )
    ''')

    # create the contexts table with context_uri as the primary key
    cur.execute('''
        CREATE TABLE IF NOT EXISTS contexts (
            context_uri TEXT PRIMARY KEY,
            context_name TEXT NOT NULL
        )
    ''')

    # create the listenings table with user_id and track_id as the foreign keys
    cur.execute('''
        CREATE TABLE IF NOT EXISTS listenings (
            user_id INTEGER NOT NULL,
            track_id INTEGER NOT NULL,
            context_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL CHECK (timestamp > 0), -- store timestamps as UNIX epoch values
            track_listens_count INTEGER NOT NULL CHECK (track_listens_count > 0),
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (track_id) REFERENCES tracks (track_id),
            FOREIGN KEY (context_id) REFERENCES contexts (context_uri)
        )
    ''')

    # add friends activity to the database
    for friend in friends_activity_json['friends']:
        # print(friend[])
        # add user to the database

        # add user_uri, user_name and user_imageUrl if the user is not in the database
        

        cur.execute("""
            INSERT OR IGNORE INTO users (user_uri, user_name, user_imageUrl)
            VALUES (?, ?, ?)
        """, (friend['user']['uri'], friend['user']['name'], friend['user']['imageUrl']))

        # get the user_id of the inserted user
        cur.execute("""
            SELECT user_id FROM users WHERE user_uri = ?
        """, (friend['user']['uri'],))
        user_id = cur.fetchone()[0]
        # add track to the database
        cur.execute("""
            INSERT OR IGNORE INTO tracks (track_uri, track_name, track_imageUrl, track_album_uri, track_album_name, track_artist_uri, track_artist_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (friend['track']['uri'], friend['track']['name'], friend['track']['imageUrl'], friend['track']['album']['uri'], friend['track']['album']['name'], friend['track']['artist']['uri'], friend['track']['artist']['name']))
        # get the track_id of the inserted track
        cur.execute("""
            SELECT track_id FROM tracks WHERE track_uri = ?
        """, (friend['track']['uri'],))
        track_id = cur.fetchone()[0]
        # add context to the database
        cur.execute("""
            INSERT OR IGNORE INTO contexts (context_uri, context_name)
            VALUES (?, ?)
        """, (friend['track']['context']['uri'], friend['track']['context']['name']))
        # check if the user has listened to the same track before
        cur.execute("""
            SELECT timestamp FROM listenings WHERE user_id = ? AND track_id = ?
        """, (user_id, track_id))
        # check if the user has listened to the same track before
        cur.execute("""
            SELECT timestamp FROM listenings WHERE user_id = ? AND track_id = ?
        """, (user_id, track_id))
        result = cur.fetchone()
        if result:
            # if yes, update the listenings table with the new timestamp and increment the track_listens_count by 1
            old_timestamp = result[0]
            new_timestamp = friend['timestamp']
            cur.execute("""
                UPDATE listenings SET timestamp = ?, track_listens_count = track_listens_count + 1 WHERE user_id = ? AND track_id = ? AND timestamp = ?
            """, (new_timestamp, user_id, track_id, old_timestamp))
        else:
            # if no, insert a new row into the listenings table with the context_id, timestamp and track_listens_count as 1
            context_id = friend['track']['context']['uri']
            timestamp = friend['timestamp']
            cur.execute("""
                INSERT INTO listenings (user_id, track_id, context_id, timestamp, track_listens_count)
                VALUES (?, ?, ?, ?, 1)
            """, (user_id, track_id, context_id, timestamp))
        
        # previous_timestamps = cur.fetchall()
        
    users = cur.fetchall()

    for i in users:
        print(i)
