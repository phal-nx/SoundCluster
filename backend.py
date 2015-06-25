#!/usr/bin/env python3
from termcolor import colored
import soundcloud
import pdb

#client = soundcloud.Client(client_id='8e906fb7c324fc6640fd3fc08ef9d1ff',client_secret='acd3a93bdfcf1dd65ed33497f091800', redirect_uri= url_for('logged_in'))
#redirect client.authorize_url()
def main():
    client = soundcloud.Client(
            client_id='8e906fb7c324fc6640fd3fc08ef9d1ff',
            client_secret='aacd3a93bdfcf1dd65ed33497f091800',
            username="phdrummer80@gmail.com",
            password="letmein"
    )
    
    print(colored(client.get('/me').username, 'red'),'is logged in')
    
    
    print( "1) Acquire Followings")
    print( "2) Print Followings ")
    command = "f" 
    while command != "q":
        command = input("Enter Command:")
        if command == "1":
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

        if command == "2":
            print('You are following', colored( client.get('/me').followings_count,'green'),'users')
            for follower in totalFollowers:
                print(follower['username'])

if __name__ == '__main__':
    main()
