#!/usr/bin/env python3
from pymongo import MongoClient
from collections import Counter
import os
import soundcloud
import getpass
import pdb



# Initializes Mongo
mongoClient = MongoClient()
db = mongoClient.soundcloud

''''
Return countries
'''
def tallyCountries(followings):
    if followings:
        artistsWithCountries = [following for following in followings if following['country']]
    else:
        artistsWithCountries = db.followings.find( { "country": { "$exists": True, "$nin": ["None"]}}, {"country":1, "_id":0})
    return Counter( [artist['country'] for artist in artistsWithCountries if artist['country'] != "None"])
    

'''
Search your likes in the DB
'''
def searchLikes(query, user_id):
    results = list(db.likes.find({"$text":{"$search":query}, "user_id": user_id}))
    return results

'''
Takes a client, updates their liked tracks in the db
'''
def updateLikes(client):
    totalLikes = list()
    # start paging through results, 200 at a time
    favorites = client.get('/me/favorites', limit=200,
                        linked_partitioning=1)
    user_id = client.get('/me/').id
    totalLikes = totalLikes + [favorite for favorite in (favorites.collection)]
    previousResult = favorites

    # if there are more than 200 followers, keeps getting them
    while hasattr(previousResult,'next_href'):
        favorites = client.get(previousResult.next_href, limit=200,linked_partitioning=1) 
        totalLikes = totalLikes + list(favorites.collection)
        previousResult = favorites
    db.likes.delete_many({"user_id":user_id})
    likes = list()
    for like in totalLikes:
        try:
            likes.append({'user_id':user_id, 'url':like.permalink_url,'username':like.user['username'],  'title': like.title, 'genre':like.genre, 'downloadable': like.downloadable, 'artwork_url' : like.artwork_url if like.artwork_url else "http://none.com",   'duration': like.duration })
        except:
            pdb.set_trace()
    if likes: 
        db.likes.insert_many(likes)
        db.likes.create_index( [('username', "text"),('genre', "text"),('title', "text")])

def getLikes(client):
    user_id = client.get('/me/').id
    likes = db.likes.find( { 'user_id': user_id } )
    return likes


'''
Takes a client, updates their uploaded tracks in the db
'''
def updateTracks(client):
    totalTracks = list()
    returnTracks = list()
    # start paging through results, 200 at a time
    tracks = client.get('/me/tracks', limit=200,
                        linked_partitioning=1)
    user_id = client.get('/me/').id
    totalTracks += [track for track in (tracks.collection)]
    totalTracks = totalTracks + list(tracks.collection)
    previousResult = tracks
    # if there are more than 200 followers, keeps getting them
    while hasattr(previousResult,'next_href'):
        tracks = client.get(previousResult.next_href, limit=200,linked_partitioning=1) 
        totalTracks = totalTracks + list(tracks.collection)
        previousResult = tracks
    db.tracks.delete_many({"user_id":user_id})

    # List Comprehension Version
    # tracks = [{'username':track.user['username'],  'title': track.title, 'genre':track.genre, 'downloadable': track.downloadable, 'artwork_url' : track.artwork_url, 'plays': track.playback_count, 'favorited':track.favoritings_count, 'duration': track.duration, 'sharing': track.sharing,'url': track.permalink_url } for track in totalTracks]
   
    #For Loop version
    for track in totalTracks:
        try:
            returnTracks.append({'user_id':user_id,'username':track.user['username'],  
            'title': track.title, 'genre':track.genre, 'downloadable': track.downloadable, 'artwork_url' : track.artwork_url, 
            'plays': track.playback_count, 'favorited':track.favoritings_count, 'duration': track.duration,
            'sharing': track.sharing,'url': track.permalink_url })
        except:
            pdb.set_trace()
    if tracks:
        db.tracks.insert_many(returnTracks)
'''
Takes a client, returns their uploaded tracks (can change to be user_id)
'''
def getTracks(client):
    user_id = client.get('/me/').id
    tracks = db.tracks.find({'user_id': user_id})
    return tracks

'''
Takes a client, updates the people you follow in the db
'''
def updateFollowings(client):
    totalFollowings = list()
    # start paging through results, 200 at a time
    followers = client.get('/me/followings', limit=200,
                        linked_partitioning=1)
    if followers.collection != None:
    	totalFollowings = totalFollowings + [follower for follower in (followers.collection)]
    previousResult = followers

    # if there are more than 200 followers, keeps getting them
    while hasattr(previousResult,'next_href') and previousResult.next_href != None:
        followers = client.get(previousResult.next_href, limit=200,linked_partitioning=1) 
        if followers.collection != None:
            totalFollowings = totalFollowings + list(followers.collection)
        previousResult = followers
    db.followings.delete_many({"user_id":user_id})

    followings = [{'username':following.username,  'country':following.country, 'full_name': following.full_name, 'city': following.city,'track_count': following.track_count, 'followers_count':following.followers_count } for following in totalFollowings]
    db.followings.insert_many(list(followings))

'''
Takes a client, returns their uploaded tracks (can change to be user_id)
'''
def getFollowings(client):
    user_id = client.get('/me/').id
    tracks = db.followings.find({'user_id': user_id})
    return tracks


