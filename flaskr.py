#!/usr/bin/env python3
from termcolor import colored
from pymongo import MongoClient
from tabulate import tabulate
from collections import Counter
from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from flask import redirect
from pymongo import MongoClient
import pprint
import os
import soundcloud
import getpass
import pdb


#scClient= soundcloud.Client(client_id='8e906fb7c324fc6640fd3fc08ef9d1ff',client_secret='acd3a93bdfcf1dd65ed33497f091800', redirect_uri= url_for('logged_in'))


app = Flask(__name__)
app.debug = True
# Initializes Mongo
mongoClient = MongoClient()
db = mongoClient.soundcloud


client = soundcloud.Client(client_id='8e906fb7c324fc6640fd3fc08ef9d1ff',
    client_secret='aacd3a93bdfcf1dd65ed33497f091800',
    redirect_uri='http://localhost:5000/profile/')#url_for('profilePage'))

@app.route('/')
def mainPage(entries=None):
    #client = soundcloud.Client(client_id='8e906fb7c324fc6640fd3fc08ef9d1ff',
    #   client_secret='aacd3a93bdfcf1dd65ed33497f091800',
    #   redirect_uri='http://localhost:5000/profile/')#url_for('profilePage'))
    return redirect(client.authorize_url())

@app.route('/profile/')
def profilePage():
    code = request.form['code']
    access_Token = client.exchange_token(code)

    client = soundcloud.Client(access_token=access_Token)
    #currentUser = client.get('/me/') 
    return render_template('profile.html')
    return render_template('profile.html', currentuser=currentUser.username )

if __name__ == '__main__':
    app.run()
