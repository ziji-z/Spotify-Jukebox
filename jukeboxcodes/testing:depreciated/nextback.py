#code for House's jukebox
#just runs the next/back button presses
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
from gpiozero import Button
from signal import pause



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

client_id = "2351925813ee44bda0e8be0507c9598c"

redirect_uri = "http://localhost:3000"
client_secret= "49d1ca3276ec47f0b7f3098fb129d91a"
state = "3jsi1owhonaf83bn" #random string
scope = "user-read-private user-read-email user-modify-playback-state user-read-playback-state user-read-currently-playing"
authorize_base = "https://accounts.spotify.com/authorize?"

#initial_auth()
#os.chdir("/Users/zijizhou/Documents/Amherst/House") #set directory
os.chdir("/home/piplayer/scripts")

token_file = open("tokens.txt","r+")
tokens = token_file.readlines()
access_token = tokens[0][:-1]
token_type = 'Bearer'
refresh_token = tokens[1][:-1]
scope = tokens[2]
token_file.close()

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
    output = response.json()

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return currently_playing()
    
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
    print("stopgo")
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
    update_now_playing()
    
def previous(): #go back
    
    base = "https://api.spotify.com/v1/me/player/previous"
    authorization = token_type + " " + access_token

    response = requests.post(base,headers={"Authorization":authorization})

    status_code_str = str(response.status_code)
    #if the token expired
    if(status_code_str == "401"):
        refresh()
        return previous()
    update_now_playing()

def toggle_play(): #play if paused, pause if playing
    playing = currently_playing()
    if playing['playing']:
        pauseplay()
    else:
        play()
        
def update_now_playing(): #edit the lcd file 
    now_playing = ""
    playing = currently_playing()

    now_playing = playing['name']
    now_playing = now_playing + " by:"
    for i in playing['artists']:
        now_playing = now_playing + " " + i
    now_playing = now_playing + "\n"
    
    f = open(r'lcd_output.txt', 'r')    # pass an appropriate path of the required file
    lines = f.readlines()
    if len(lines) > 0:
        lines[0] = now_playing    # n is the line number you want to edit; subtract 1 as indexing of list starts from 0
    else:
        lines.append
    f.close()   # close the file and reopen in write mode to enable writing to file; you can also open in append mode and use "seek", but you will have some unwanted old data if the new data is shorter in length.

    f = open(r'lcd_output.txt', 'w')
    f.writelines(lines)
    # do the remaining operations on the file
    f.close()

#def get_playlists(): #get a list of playlists

buttonnext = Button(3)
buttonback = Button(4)

buttonback.when_pressed = previous
buttonnext.when_pressed = next

pause()
