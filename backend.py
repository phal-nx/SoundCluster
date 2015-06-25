#!/usr/bin/env python3
from termcolor import colored
import soundcloud

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
    print( "1) Print all Following")
    command = input("Enter Command:")
    if command == "1":
        count = 50  # Loops through followers because rate limited to 50
        newFollowers = client.get('/me/followings/')
        followers = newFollowers
        while len( newFollowers ) >= 50:
            newFollowers = client.get('me/followings/', offset=count)
            followers + newFollowers
            count= count+50

        print('You are following', colored( client.get('/me').followings_count,'green'),'users')
        for follower in followers:
            print(follower.username)

if __name__ == '__main__':
    main()
