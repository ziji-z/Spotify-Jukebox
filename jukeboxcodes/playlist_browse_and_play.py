#code for House's jukebox
#fetches the list of playlists on a certain account, browses through them, and can shuffle through the playlist
#ziji april/29

import socket
import time
#api stuff
import requests
import json
import sys
import random
import base64
import urllib.request
import os
#from gpiozero import whatever an encoder works



def initial_auth(): #initial authorization, no need to use unless something goes wrong
    url = authorize_base + "response_type=code&client_id=" + client_id + "&scope=" + scope + "&redirect_uri=" + redirect_uri + "&state=" + state
    #print(url)

    response = requests.get(authorize_base,params = {"response_type": "code","client_id":client_id,"scope":scope,"redirect_uri":redirect_uri,"state":state},allow_redirects=True)
    r = requests.head(response.url, allow_redirects=True)
    print(r.url)

    code = input("code= ")

    grant_type = "authorization_code"
    content_type = "application/x-www-form-urlencoded"

    base = "https://accounts.spotify.com/api/token"

    authorization = base64.b64encode((client_id+":"+client_secret).encode("ascii")).decode("ascii")

    response = requests.post(base,headers={"content-type":content_type,"Authorization":"Basic " + authorization},data={"code":code,"redirect_uri":redirect_uri,"grant_type":grant_type})

    print(response.json())
    
    stop = input("continue? y/n")
    if stop == "n":
        sys.exit()




client_id = "4de989c4e3c54f1fa77fc01092568e6c"

redirect_uri = "http://localhost:3000"
client_secret= "46caa4b6e17a40bfa3e3e63d87acbc97"
state = "3jsi1owhonaf83bnh" #random string
scope = "user-read-private user-read-email user-modify-playback-state user-read-playback-state user-read-currently-playing"
authorize_base = "https://accounts.spotify.com/authorize?"

#initial_auth()
os.chdir(os.path.dirname(__file__))


token_file = open("tokens.txt","r+")
tokens = token_file.readlines()
access_token = tokens[0][:-1]
token_type = 'Bearer'
refresh_token = tokens[1][:-1]
scope = tokens[2]
token_file.close()

playlists = [] #store each playlist in a list of dictionaries

def refresh(): #if the token expired, uses the refresh token to get a new access token
    #each authorization only lasts 60 minutes, so we need to refresh every hour
    #set up the authorizations
    authorization = base64.b64encode((client_id+":"+client_secret).encode("ascii")).decode("ascii")
    base = "https://accounts.spotify.com/api/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "Authorization":'Basic ' + authorization
    }
    data = {
        'grant_type':"refresh_token",
        'refresh_token':refresh_token,
    }
    #call the authorization
    response = requests.post(base,headers=headers,data=data)
    output = response.json()
    
    #print(output)
    #print(output['access_token'])
    
    #save the authorization
    token_file = open("tokens.txt","w")
    global access_token
    global scope
    access_token = output["access_token"]
    scope = output["scope"]
    
    token_file.write(access_token+"\n"+refresh_token+"\n"+scope)
    token_file.close

def get_devices(): #get a list of devices that can playback, useful to force sound on the webplayer, and returns the device ID of the webplayer
    base = "https://api.spotify.com/v1/me/player/devices"
    authorization = token_type + " " + access_token

    response = requests.get(base,headers={"method":"GET","Authorization":authorization})
    output = response.json()

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return get_devices()
    
    for i in output['devices']:
        #print(i['name'])
        #print(i['type'])
        if 'Web Player' in i['name']:
            device_id = i['id']
            return device_id
    return 0 #otherwise return 0

def currently_playing(): #returns a dictionary of the current song name and all the artists attributed
    base = "https://api.spotify.com/v1/me/player"
    authorization = token_type + " " + access_token

    response = requests.get(base,headers={"method":"GET","Authorization":authorization})    

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return currently_playing()
    
    if (status_code_str == "204"):
        song = {
        'playing': False,
        'name': 'Nothing Playing',
        'artists': "none"
        }  
        return song    
    output = response.json()
    #in case of multiple artists
    artists = []
    for i in output['item']['artists']:
        artists.append(i['name'])
    
    #create the dictionary
    song = {
        'playing': output['is_playing'],
        'name': output['item']['name'],
        'artists': artists
    }
    return song

def transer_playback(device = str): #transfer the playback to device by id
    base = "https://api.spotify.com/v1/me/player"
    authorization = token_type + " " + access_token

    headers = {
        'method':"PUT",
        'Authorization':authorization
    }
    data = {
        'device_ids':[device]
    }
    response = requests.put(base,headers=headers,json=data)

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        transer_playback(device)
        return

def play(): #resume play
    base = "https://api.spotify.com/v1/me/player/play"
    authorization = token_type + " " + access_token

    response = requests.put(base,headers={"Authorization":authorization})

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return play()
    
def pauseplay(): #pause play
    base = "https://api.spotify.com/v1/me/player/pause"
    authorization = token_type + " " + access_token

    response = requests.put(base,headers={"Authorization":authorization})

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return pauseplay()

def next(): #skip
    base = "https://api.spotify.com/v1/me/player/next"
    authorization = token_type + " " + access_token

    response = requests.post(base,headers={"Authorization":authorization})

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return next()
    
def previous(): #go back
    base = "https://api.spotify.com/v1/me/player/previous"
    authorization = token_type + " " + access_token

    response = requests.post(base,headers={"Authorization":authorization})

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return previous()

def toggle_play(): #play if paused, pause if playing
    playing = currently_playing()
    if playing['playing']:
        pauseplay()
    else:
        play()

def get_playlists(): #get a list of playlists of the current user
    playlists.clear() #empties the list first
    base = "https://api.spotify.com/v1/me/playlists"
    authorization = token_type + " " + access_token

    response = requests.get(base,headers={"Authorization":authorization},params={'limit':50})
    output = response.json()
    
    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return get_playlists()
    
    for i in range(len(output['items'])):
        playlists.append(output['items'][i])

def play_playlist(theplaylist): #shuffles the playlist dictionary that's passed through
    base = "https://api.spotify.com/v1/me/player/play"
    authorization = token_type + " " + access_token
    
    topend = int(theplaylist['tracks']['total'])-1 #randomizes where the playlist starts, need to cap it at 0 in case the playlist is empty
    if topend < 0:
        return #doesn't let you do anything if it's empty
    offset = random.randint(0,topend)#sets the offset
    
    body = {
        'context_uri':theplaylist['uri'],
        'offset':{'position':offset}
    }

    response = requests.put(base,headers={"Authorization":authorization},json=body)

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return play_playlist(theplaylist)
    
    turn_on_shuffle() #then turn on shuffle by default
    
def turn_on_shuffle(): #turns on shuffle
    base = "https://api.spotify.com/v1/me/player/shuffle"
    authorization = token_type + " " + access_token

    response = requests.put(base,headers={"Authorization":authorization},params={'state':'true'})

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return turn_on_shuffle()

def update_now_playing(): #edit the lcd file 
    now_playing = ""
    playing = currently_playing()

    now_playing = playing['name']
    artists = ""
    
    seperator = " "
    artists = seperator.join(playing['artists'])

        
    now_playing = now_playing + '\n' #add the line breaks for artists and song name
    artists = artists + "\n"
            
    f = open(r'lcd_output.txt', 'r')    # pass an appropriate path of the required file
    lines = f.readlines()
    #print(lines)
    lines[0] = now_playing    # n is the line number you want to edit; subtract 1 as indexing of list starts from 0
    lines[1] = artists
    f.close()   # close the file and reopen in write mode to enable writing to file; you can also open in append mode and use "seek", but you will have some unwanted old data if the new data is shorter in length.

    f = open(r'lcd_output.txt', 'w')
    #print(lines[0]+lines[1])
    lines[3] = "10"
    f.write(lines[0]+lines[1]+lines[2]+lines[3])
    # do the remaining operations on the file
    f.close()

def display_playlist(name): #change the display of the second line
    #print(name)
    f = open(r'lcd_output.txt', 'r')    # pass an appropriate path of the required file
    lines = f.readlines()
    #print(lines)
    f.close()   # close the file and reopen in write mode to enable writing to file; you can also open in append mode and use "seek", but you will have some unwanted old data if the new data is shorter in length.
    
    f = open(r'lcd_output.txt', 'w') #line 2 gives the playlist name, line 3 states whether to display playlist name, if 0 then yes
    lines[2] = name + "\n"
    lines[3] = 0
    #print(lines[0]+lines[1])
    f.write(lines[0]+lines[1]+lines[2]+str(lines[3]))
    # do the remaining operations on the file
    f.close()

get_playlists() #get the list of playlists

current_selection = 0
while True:
    display_playlist(playlists[current_selection]["name"])
    selection = input("currently selected: " + playlists[current_selection]["name"] + ", 1 to go back, 2 to go forward, 0 to shuffle this playlist")
    #replace this with just the playlist display obviously
    
    match selection: #and this with the encoder
        case "1":
            current_selection = current_selection - 1
            if current_selection < 0:
                current_selection = len(playlists)-1
        case "2":
            current_selection = (current_selection + 1)%len(playlists)
        case "0":
            play_playlist(playlists[current_selection])
            update_now_playing()
            display_playlist(playlists[current_selection]["name"])
            print('now playing ' + currently_playing()['name'] + " from the playlist " + playlists[current_selection]["name"])