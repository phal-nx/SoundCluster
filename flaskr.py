#!/usr/bin/env python3
from termcolor import colored
from pymongo import MongoClient
from tabulate import tabulate
from collections import Counter
from flask import Flask
from flask import render_template
from flask import url_for
from flask import escape
from flask import request
from flask import redirect
from flask import session
from pymongo import MongoClient
import pprint
import os
import soundcloud
import getpass
import pdb
import backend

app = Flask(__name__)
app.debug = True

# Initializes Mongo
mongoClient = MongoClient()
db = mongoClient.soundcloud

client = soundcloud.Client(client_id='8e906fb7c324fc6640fd3fc08ef9d1ff',
    client_secret='aacd3a93bdfcf1dd65ed33497f091800',
    redirect_uri='http://1e925256.ngrok.io/authenticate')

@app.route('/')
def mainPage(entries=None):
    if 'access_token' in session:
        return redirect(url_for('profilePage'))
    return redirect(client.authorize_url())

@app.route('/authenticate')
def authenticate():
    #client = soundcloud.Client(client_id='8e906fb7c324fc6640fd3fc08ef9d1ff',
    #    client_secret='aacd3a93bdfcf1dd65ed33497f091800',
    #    redirect_uri='http://localhost:5000/profile')#url_for('profilePage'))
    code = request.args.get('code')
    token = client.exchange_token(code)
    session['access_token'] = token.access_token
    #for x in (attribute for attribute in dir(client.get('/me')) if not attribute.startswith('__')):
        #if type(x) == 'str':
    #    session[x] = str(client.get('/me').x)
    return redirect(url_for('profilePage'))

@app.route('/logout')
def logout():
    session.pop('access_token',None)
    return redirect(url_for('mainPage'))

@app.route('/profile')
def profilePage():
    if 'access_token' not in session:
        return redirect(url_for('mainPage'))
    accessTok = session['access_token']
    newClient = soundcloud.Client(access_token=accessTok)
    backend.updateLikes(newClient)
    backend.updateTracks(newClient)
    currentLikes = backend.getLikes(newClient) #newClient.get('/me/favorites')
    currentTracks = backend.getTracks(newClient) #newClient.get('/me/tracks')
    currentUser = newClient.get('/me') 
    followings = backend.getFollowings(newClient)
    countries = backend.tallyCountries(followings)
    return render_template('profile.html', user=currentUser, likes = currentLikes, tracks = currentTracks, countryTally = countries )

@app.route('/search', methods=[ 'GET'])
def searchPage():
    if 'access_token' not in session:
        return redirect(url_for('mainPage'))
    accessTok = session['access_token']
    newClient = soundcloud.Client(access_token=accessTok) 
    currentUser = newClient.get('/me')
    query = request.args.get('filterLikes')
    currentLikes = backend.searchLikes(query, currentUser.id) 
    currentTracks = backend.getTracks(newClient)
    return render_template('profile.html', user=currentUser, likes = currentLikes, tracks = currentTracks)

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?QQ'
    app.run()
