#/user/bin/env python3
from termcolor import colored
from tabulate import tabulate
from collections import Counter
#from pymongo import mongoClient
from backend import *
import pprint
import os
import soundcloud
import getpass
import pdb

#db = mongoClient.soundcloud


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
            printCountries()

        if command == "6":
            query = input("Enter a query: ")
            searchLikes(client.get('/me/').id, query)
'''
Print countries in terminal
'''
def printCountries():
    artistsWithCountries = db.followings.find( { "country": { "$exists": True, "$nin": ["None"]}}, {"country":1, "_id":0})
    pprint.pprint(Counter([ artist['country'] for artist in artistsWithCountries if artist['country'] != "None"]))

    

'''
Print your likes in the terminal
'''
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

'''
Print all followings in terminal
'''
def printFollowings(client):
    print('You are following', colored( client.get('/me').followings_count,'green'),'users')
    followings = db.followings.find()
    table = [[follower['username'],  follower['country'], follower['followers_count']]   for follower in followings]
    headers=["Username", "Country", "Followers"]
    print(tabulate(table, headers, tablefmt="fancy_grid"))

'''
Print all tracks in terminal
'''
def printTracks(client):
    tracks = db.tracks.find()
    #print('You are following', colored( len(tracks),'green'),'users')
    table = [[track['sharing'],  track['title'], track['genre']]   for track in tracks]
    headers=["Sharing", "Title", "Followers"]
    print(tabulate(table, headers, tablefmt="fancy_grid"))

'''
Print all likes in terminal
'''
def printLikes(client):
    favorites = db.likes.find()
    print('You have liked', colored( client.get('/me').public_favorites_count,'green'),'tracks')
    table = [[favorite['username'],  favorite['title'][:25], favorite['genre']]   for favorite in favorites]
    headers=["Username", "Title", "Genre"]
    print(tabulate(table, headers, tablefmt="grid"))

if __name__ == '__main__':
    main()
