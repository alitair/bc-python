import requests
import json


# Grab your uid from the python section of https://birdcallauth.web.app
api_request = {"uid": "API KEY HERE"} 
host        = "https://birdcallauth.web.app"

# if you are running the birdconv server locally, use this instead
# host        = "http://localhost:5173"

active_path = '/api/active'
room_path   = '/api/room'
token_path  = '/api/token_monitor'
headers     = {'Content-Type': 'application/json'}


# choose printIt=True to see the request and response from the api
def send_request( path, api_request, printit=True) :

    if printit:
        print("Request to " + path)
        print(json.dumps(api_request, indent=4))

    response = requests.post( host + path, headers=headers, json=api_request)
    if response.ok:
        res = response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")

    if printit:
        print("Response:")
        print(json.dumps(res, indent=4))
    return res

# Get a list of active devices in birdconv
def active():
    return send_request(active_path, api_request, printit=False)

# create a room with a subset of the active devices
def create_room( devices , recording=False, expiryTime=1):
    roomRequest = {
        "devices"    : devices, # A subset of the array of devices returned by the /active endpoint
        "audioOnly"  : False, # this value is ignored, 
        "recording"  : recording, # set to True to record
        "expiryTime" : expiryTime*60,    # how long the call will be active, 1 min * 60 sec
    }
    roomRequest.update(api_request)

    return send_request(room_path, roomRequest, printit=False)

# get a token for this program to join a room
def create_token( room  , username):

    device = {
        "username"   : username,  # here is your python program's name
        "species"    : "computer",  # use computer
        "deviceId"   : "",  # !! leave blank !!
        "fcm_token"  : "",  # !! leave blank !!
    }
    device.update(api_request)

    token_request = {
        "device" : device,
        "eavesdrop" : False # this way you are allowed to send video and audio!
    }
    token_request.update(room)
    token_request.update(api_request)

    return send_request(token_path, token_request, printit=False)