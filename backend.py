#!/usr/bin/env python3
from termcolor import colored
from pymongo import MongoClient
from tabulate import tabulate
from collections import Counter
import pprint
import os
import soundcloud
import getpass
import pdb


#scClient= soundcloud.Client(client_id='8e906fb7c324fc6640fd3fc08ef9d1ff',client_secret='acd3a93bdfcf1dd65ed33497f091800', redirect_uri= url_for('logged_in'))
#redirect client.authorize_url()

# Initializes Mongo
mongoClient = MongoClient()
db = mongoClient.soundcloud

def main():
    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')



    # Welcome Message
    print(colored("####################", "cyan"))
    print(colored("SoundCluster, v 0.1","cyan")) 
    print(colored("Made by Phil Leonowens","cyan")) 
    print(colored("####################", "cyan"))
    # 

    scUsername = input(colored("Soundcloud Username:", "blue"))
    scPass = getpass.getpass(colored("Password:","blue"))

    command = "f" 
    try:
        scClient = soundcloud.Client(
            client_id='8e906fb7c324fc6640fd3fc08ef9d1ff',
            client_secret='aacd3a93bdfcf1dd65ed33497f091800',
            username=scUsername,
            password=scPass
    )
        print(colored(scClient.get('/me').username, 'red'),'is logged in')
        print( "1) Acquire Followings")
        print( "2) Acquire Likes ")
        print( "3) Print Followings ")
        print( "4) Print Likes ")
        print( "5) Tally Countries")
        print( "6) Search Likes")
    except:
        print(colored("Incorrect Login", "white","on_red"))
        command="q"
    while command != "q":
        command = input("Enter Command:")
        if command == "1":
            updateFollowings(scClient)

        if command == "2":
            updateLikes(scClient)

        if command == "2a":
            updateTracks(scClient)
        if command == "2b":
            printTracks(scClient)

        if command == "3":
            printFollowings(scClient)

        if command == "4":
            printLikes(scClient)
       
        if command == "5":
            tallyCountries()

        if command == "6":
            query = input("Enter a query: ")
            searchLikes(query)

def tallyCountries():
    artistsWithCountries = db.followings.find( { "country": { "$exists": True, "$nin": ["None"]}}, {"country":1, "_id":0})
    pprint.pprint(Counter([artist['country'] for artist in artistsWithCountries if artist['country'] != "None"]))

def printLikes(query):
    results = list(db.likes.find({"$text":{"$search":query}}))
    if len(results) > 0:
        table = [[favorite['username'],  favorite['title'][:25], favorite['genre']]   for favorite in results]    
        headers=["Artist", "Title", "Genre"]
        print(tabulate(table,headers))
        if len(results)>1:
            print(colored(str(len(results)) + " results found",'green'))
        else:
            print(colored("1 result found", 'green'))
    else:
        print(colored("No Results Found"),'red')
    

def searchLikes(query):
    results = list(db.likes.find({"$text":{"$search":query}}))
    return results

def printFollowings(client):
    print('You are following', colored( client.get('/me').followings_count,'green'),'users')
    followings = db.followings.find()
    table = [[follower['username'],  follower['country'], follower['followers_count']]   for follower in followings]
    headers=["Username", "Country", "Followers"]
    print(tabulate(table, headers, tablefmt="fancy_grid"))

def printTracks(client):
    tracks = db.tracks.find()
    #print('You are following', colored( len(tracks),'green'),'users')
    table = [[track['sharing'],  track['title'], track['genre']]   for track in tracks]
    headers=["Sharing", "Title", "Followers"]
    print(tabulate(table, headers, tablefmt="fancy_grid"))


def printLikes(client):
    favorites = db.likes.find()
    print('You have liked', colored( client.get('/me').public_favorites_count,'green'),'tracks')
    table = [[favorite['username'],  favorite['title'][:25], favorite['genre']]   for favorite in favorites]
    headers=["Username", "Title", "Genre"]
    print(tabulate(table, headers, tablefmt="grid"))

def updateLikes(client):
    totalLikes = list()
    # start paging through results, 200 at a time
    favorites = client.get('/me/favorites', limit=200,
                        linked_partitioning=1)
    totalLikes = totalLikes + [favorite for favorite in (favorites.collection)]
    previousResult = favorites

    # if there are more than 200 followers, keeps getting them
    while hasattr(previousResult,'next_href'):
        favorites = client.get(previousResult.next_href, limit=200,linked_partitioning=1) 
        totalLikes = totalLikes + list(favorites.collection)
        previousResult = favorites
    db.likes.drop()
    likes = [{'url':like.permalink_url,'username':like.user['username'],  'title': like.title, 'genre':like.genre, 'downloadable': like.downloadable, 'artwork_url' : like.artwork_url if like.artwork_url else "http://none.com", 'plays': like.playback_count, 'favorited':like.favoritings_count, 'duration': like.duration }   for like in totalLikes ]# if hasattr(like, 'username') and hasattr(like, 'title') and hasattr(like, 'genre') and hasattr(like, 'downloadable') and hasattr(like, 'artwork_url') and hasattr(like, 'plays') and hasattr(like, 'favorited') and hasattr(like, 'duration')]
    if likes: 
        db.likes.insert_many(likes)
        db.likes.create_index( [('username', "text"),('genre', "text"),('title', "text")])

def getLikes(client):
    likes = db.likes.find()
    return likes

def updateTracks(client):
    totalTracks = list()
    # start paging through results, 200 at a time
    tracks = client.get('/me/tracks', limit=200,
                        linked_partitioning=1)
    totalTracks += [track for track in (tracks.collection)]
    totalTracks = totalTracks + list(tracks.collection)
    previousResult = tracks
    # if there are more than 200 followers, keeps getting them
    while hasattr(previousResult,'next_href'):
        tracks = client.get(previousResult.next_href, limit=200,linked_partitioning=1) 
        totalTracks = totalTracks + list(tracks.collection)
        previousResult = tracks
    db.tracks.drop()
    tracks = [{'username':track.user['username'],  'title': track.title, 'genre':track.genre, 'downloadable': track.downloadable, 'artwork_url' : track.artwork_url, 'plays': track.playback_count, 'favorited':track.favoritings_count, 'duration': track.duration, 'sharing': track.sharing,'url': track.permalink_url } for track in totalTracks]
    if tracks:
        db.tracks.insert_many(tracks)

def getTracks(client):
    tracks = db.tracks.find()
    return tracks

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
    db.followings.drop()

    followings = [{'username':following.username,  'country':following.country, 'full_name': following.full_name, 'city': following.city,'track_count': following.track_count, 'followers_count':following.followers_count } for following in totalFollowings]
    db.followings.insert_many(list(followings))


if __name__ == '__main__':
    main()
