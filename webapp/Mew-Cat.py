import sqlite3
# import flask and jsonify
from flask import Flask, jsonify
from flask import render_template
from flask import Flask, render_template, request, session, redirect
# import the FriendActivityAnaliser class
from main import FriendActivityAnaliser

# create an instance of the Flask app
# app = Flask(__name__)
app = Flask(__name__, template_folder="templets")

# create an instance of the FriendActivityAnaliser class with the database name
faa = FriendActivityAnaliser("friends_activity.db")

# define a route for the top tracks endpoint
@app.route("/top_tracks")
def top_tracks():
    # get the query parameters from the request
    user_id = request.args.get("user_id")
    time_period = request.args.get("time_period")
    by_artist_uri = request.args.get("by_artist_uri")
    by_album_uri = request.args.get("by_album_uri")
    limit = request.args.get("limit")

    # convert the query parameters to the appropriate types
    if user_id:
        # if user_id is a comma-separated list of values, split it and convert each value to int
        if "," in user_id:
            user_id = [int(x) for x in user_id.split(",")]
        # otherwise, convert user_id to int
        else:
            user_id = int(user_id)
    
    if time_period:
        # if time_period is a dash-separated range of values, split it and keep it as a tuple of strings
        if "-" in time_period:
            time_period = tuple(time_period.split("-"))
        # otherwise, keep time_period as a string
    
    if by_artist_uri:
        # if by_artist_uri is a comma-separated list of values, split it and keep it as a list of strings
        if "," in by_artist_uri:
            by_artist_uri = by_artist_uri.split(",")
    
    if by_album_uri:
        # if by_album_uri is a comma-separated list of values, split it and keep it as a list of strings
        if "," in by_album_uri:
            by_album_uri = by_album_uri.split(",")

    if limit:
        # convert limit to int
        limit = int(limit)

    # call the top_tracks method of the faa object with the query parameters
    data = faa.top_tracks(user_id, time_period, by_artist_uri, by_album_uri, limit)

    # return the data as a JSON response with status code 200
    return jsonify(data), 200

@app.route("/")
def index():
    # define data by calling the top_tracks method with some default parameters
    # you can change these parameters as you wish
    data = faa.top_tracks(user_id=7, limit=1)
    # check if data is not None before passing it to the template
    if data is not None:

        song = {
            "user_name": song_tuple[0],
            "spotify_url": song_tuple[1],
            "name": song_tuple[2],
            "artist_url": song_tuple[3],
            "album_url": song_tuple[4],
            "album_name": song_tuple[5],
            "count": song_tuple[6]
        }
        
        # pass the songs list to the template instead of data
        return render_template("index.html", data=songs)
    # otherwise, return an error message or a default page
    else:
        return "Sorry, no data found for the given parameters."

# data = faa.top_tracks(user_id=7, limit=1)
# # check if data is not None before passing it to the template
# if data is not None:
#     # create an empty list to store the song objects
#     songs = []
#     # loop through the data and create a song object for each tuple
#     for song_tuple in data:
#         # create a song object with attributes from the tuple
#         # you can use namedtuple or dict or any other data structure you prefer
#         # I'm using namedtuple here for simplicity
#         from collections import namedtuple
#         Song = namedtuple("Song", ["user_name", "spotify_url", "name", "artist_url", "album_url", "album_name", "count"])
#         song = Song(*song_tuple)
#         # append the song object to the songs list
#         songs.append(song)
# print(songs)

# run the app in debug mode
if __name__ == "__main__":
    app.run(debug=True)
