import time
import sqlite3
import main

# get the friends activity json from the main.py
friends_activity_json = main.get_friends_activity_json()


# Create a SQLite database file.
conn = sqlite3.connect('friends_activity.sqlite')

# Connect to the SQLite database.
cur = conn.cursor()

# Check if the table exists.
cur.execute('''
SELECT name
FROM sqlite_master
WHERE type = 'table'
AND name = 'friends_activity'
''')

# Store the result of fetchone() in a variable.
result = cur.fetchone()

# If the result is None, create the table.
if result is None:
    cur.execute('''CREATE TABLE friends_activity ( user_uri TEXT, track_uri TEXT, timestamp TEXT, current_time TEXT)''')

current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# fetch result from the database
# result = cur.execute('''SELECT * FROM friends_activity''')
result = cur.fetchall()


# print the result
for row in result:
    print(row)


# Insert the data into the table.
# for friend in friends_activity_json['friends']:
#   cur.execute('''
#   INSERT INTO friends_activity (user_uri, track_uri, timestamp, current_time)
#   VALUES (?, ?, ?, ?)
#   ''', (friend['user']['uri'], friend['track']['uri'], friend['timestamp'], current_time))

# Close the connection to the SQLite database.
conn.close()