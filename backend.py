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

        if command == "3":
            printFollowings(scClient)

        if command == "4":
            printLikes(scClient)
       
        if command == "5":
            tallyCountries()

        if command == "6":
            query = input("Enter a phrase")
            searchLikes(query)

def tallyCountries():
    artistsWithCountries = db.followings.find( { "country": { "$exists": True, "$nin": ["None"]}}, {"country":1, "_id":0})
    pprint.pprint(Counter([artist['country'] for artist in artistsWithCountries if artist['country'] != "None"]))

def searchLikes(query):
    results = db.likes.find(
    {"$or":[
        {"title": query},
    ]}
    )
    table = [[favorite['user']['username'],  favorite['title'][:25], favorite['genre']]   for favorite in results]
    print(tabulate(table))
    

def printFollowings(client):
    print('You are following', colored( client.get('/me').followings_count,'green'),'users')
    followings = db.followings.find()
    table = [[follower['username'],  follower['country'], follower['followers_count']]   for follower in followings]
    headers=["Username", "Country", "Followers"]
    print(tabulate(table, headers, tablefmt="fancy_grid"))

def printLikes(client):
    favorites = db.likes.find()
    print('You have liked', colored( client.get('/me').public_favorites_count,'green'),'tracks')
    table = [[favorite['user']['username'],  favorite['title'][:25], favorite['genre']]   for favorite in favorites]
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
    db.likes.insert_many(totalLikes)
    db.collection.createIndex(
            { "$**": "text" },
            { "name": "TextIndex" }
    )

def updateFollowings(client):
    totalFollowers = list()
    # start paging through results, 200 at a time
    followers = client.get('/me/followings', limit=200,
                        linked_partitioning=1)
    totalFollowers = totalFollowers + [follower for follower in (followers.collection)]
    previousResult = followers

    # if there are more than 200 followers, keeps getting them
    while hasattr(previousResult,'next_href'):
        followers = client.get(previousResult.next_href, limit=200,linked_partitioning=1) 
        totalFollowers = totalFollowers + list(followers.collection)
        previousResult = followers
    db.followings.drop()
    db.followings.insert_many(totalFollowers)


if __name__ == '__main__':
    main()
