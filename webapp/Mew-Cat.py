import sqlite3
# import flask and jsonify
from flask import Flask, jsonify
from flask import render_template
from flask import Flask, render_template, request, session, redirect
# import the FriendActivityAnaliser class
from main import FriendActivityAnaliser, get_recommendations

# create an instance of the Flask app
# app = Flask(__name__)
app = Flask(__name__, template_folder="templets")

# create an instance of the FriendActivityAnaliser class with the database name
faa = FriendActivityAnaliser("friends_activity.db")

# define a route for the home page
@app.route('/')
def home():
    # render the home.html template
    return render_template('index.html')

# define a route for the recommendations page
@app.route('/recommendations')
def recommendations():
    # get the seed artists, genres and tracks from the request parameters
    seed_artists = request.args.get('seed_artists')
    seed_genres = request.args.get('seed_genres')
    seed_tracks = request.args.get('seed_tracks')

    # if any of the parameters are missing or empty, return an error message
    if not seed_artists or not seed_genres or not seed_tracks:
        return jsonify({'error': 'Please provide seed artists, genres and tracks'})

    # split the parameters by comma and convert them to lists
    seed_artists = seed_artists.split(',')
    seed_genres = seed_genres.split(',')
    seed_tracks = seed_tracks.split(',')

    # call the get_recommendations function with the lists and get the result
    result = get_recommendations(seed_artists, seed_genres, seed_tracks)

    # return the result as a json response
    return jsonify(result)

# run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True)
