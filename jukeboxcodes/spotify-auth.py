#the initial authorization for new accounts
#ziji august/4/2024

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

def initial_auth(): #initial authorization, no need to use unless something goes wrong
    global scope
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
    
    output = response.json()
    
    #print(output)
    #print(output['access_token'])
    
    #save the authorization
    token_file = open("tokens.txt","w")
    access_token = output["access_token"]
    refresh_token = output["refresh_token"]
    scope = output["scope"]
    
    token_file.write(access_token+"\n"+refresh_token+"\n"+scope)
    token_file.close
    print("done")
    
client_id = "4de989c4e3c54f1fa77fc01092568e6c"

redirect_uri = "http://localhost:3000"
client_secret= "46caa4b6e17a40bfa3e3e63d87acbc97"
state = "3jsi1owhonaf83bnh" #random string
scope = "user-read-private user-read-email user-modify-playback-state user-read-playback-state user-read-currently-playing"
authorize_base = "https://accounts.spotify.com/authorize?"


initial_auth()
os.chdir(os.path.dirname(__file__)) #set directory
print(os.getcwd())
#os.chdir("/home/piplayer/scripts")
