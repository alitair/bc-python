import requests
import json
from daily import *

from PIL import Image
import time
import threading
import birdconv




class  Participant:
    def __init__(self, image_file, framerate):
        self.__image = Image.open(image_file)
        self.__framerate = framerate

        self.__camera = Daily.create_camera_device("my-camera",
                                                   width=self.__image.width,
                                                   height=self.__image.height,
                                                   color_format="RGB")

        self.__client = CallClient()

        self.__client.update_subscription_profiles({
            "base": {
                "camera": "unsubscribed",
                "microphone": "unsubscribed"
            }
        })

        self.__app_quit = False
        self.__app_error = None

        self.__start_event = threading.Event()
        self.__thread = threading.Thread(target=self.send_image)
        self.__thread.start()

    def on_joined(self, data, error):
        if error:
            print(f"Unable to join meeting: {error}")
            self.__app_error = error
        self.__start_event.set()

    def run(self, meeting):
        self.__client.join(meeting["url"], meeting_token=meeting["token"], client_settings={
            "inputs": {
                "camera": {
                    "isEnabled": True,
                    "settings": { "deviceId": "my-camera"}
                },
                "microphone": False
            }
        }, completion=self.on_joined)
        self.__thread.join()

    def leave(self):
        self.__app_quit = True
        self.__thread.join()
        self.__client.leave()
        self.__client.release()

    def send_image(self):
        self.__start_event.wait()

        if self.__app_error:
            print(f"Unable to send!")
            return

        sleep_time = 1.0 / self.__framerate
        image_bytes = self.__image.tobytes()

        while not self.__app_quit:
            self.__camera.write_frame(image_bytes)
            time.sleep(sleep_time)



def main():


    # set api_key
    birdconv.api_request["uid"] = "API KEY HERE"

    # get the list of birdconv devices
    devices  = birdconv.active()

    # pick the devices that you want to place in a call
    my_device = None
    for device in devices :
        if device["username"] == "Alistair":
            my_device = device
            break
    
    # place 1 or more selected devices on a call
    room  = birdconv.create_room( [my_device] ) 

    # get a token so that this python program can join the call
    meeting = birdconv.create_token( room ,  "show_image.py" )
    print("Meeting URL: "   + meeting["url"])
    # print("Meeting Token: " + meeting["token"])

    print("sleeping for 5 seconds")
    time.sleep(5)

    print("connecting...")
    Daily.init()

    print("showing a picture of a bird")
    participant = Participant("bird.png", 30)

    try:
        participant.run(meeting)
    except KeyboardInterrupt:
        print("Ctrl-C detected. Exiting!")
    finally:
        participant.leave()


if __name__ == "__main__":
    main()