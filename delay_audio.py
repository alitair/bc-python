import threading
import queue
import time
import birdconv
from   daily import *



BUFFER  = 2 # 2 second of buffering

SAMPLE_RATE = 16000
NUM_CHANNELS = 1
BYTES_PER_SAMPLE =2


class AudioApp:
    def __init__(self, sample_rate, num_channels):

        self._sample_rate  = sample_rate
        self._num_channels = num_channels
        self._client = CallClient()
        self._client.update_subscription_profiles({
            "base": {
                "camera": "unsubscribed",
                "microphone": "subscribed"
            }
        })

        self._mic_device     = Daily.create_microphone_device("my-mic" ,sample_rate=sample_rate,channels=num_channels)
        self._speaker_device = Daily.create_speaker_device("my-speaker",sample_rate=sample_rate,channels=num_channels)
        Daily.select_speaker_device("my-speaker")

        self.client_settings = {
            "inputs": {
                "camera": False,
                "microphone": {
                    "isEnabled": True,
                    "settings": {
                        "deviceId": "my-mic"
                    }
                }
            }
        }

        self._app_quit = False
        self._app_error = None

        self._buffer_queue = queue.Queue()

        self._start_receive_event = threading.Event()
        self._thread_receive      = threading.Thread(target=self.receive_audio)
        self._thread_receive.start()

        self._start_send_event = threading.Event()
        self._thread_send       = threading.Thread(target=self.send_audio)
        self._thread_send.start()


    def on_joined(self, data, error):
        if error:
            print(f"Unable to join meeting: {error}")
            self._app_error = error
        self._start_receive_event.set()
        self._start_send_event.set()

    def run(self, meeting):
        meeting_url  = meeting["url"]
        meeting_token = meeting["token"]
        self._client.join(meeting_url, meeting_token=meeting_token, client_settings=self.client_settings, completion=self.on_joined)

        # wait until both threads terrminate 
        self._thread_receive.join()
        self._thread_send.join()

    def leave(self):
        self._app_quit = True
        self._thread_receive.join()
        self._thread_send.join()
        self._client.leave()
        self._client.release()


    def receive_audio(self):
        self._start_receive_event.wait()
        print("starting receive audio thread")

        if self._app_error:
            print("Unable to receive audio!")
            return

        while not self._app_quit:
            # Read BUFFER seconds worth of audio frames.
            num_frames = int(self._sample_rate * BUFFER)
            buffer = self._speaker_device.read_frames(num_frames)

            if buffer:
                self._buffer_queue.put(buffer) 

    def send_audio(self):
        self._start_send_event.wait()
        print("starting send audio thread")


        if self._app_error:
            print("Unable to send audio!")
            return

        while not self._app_quit:
            try:
                # Wait for BUFFER seconds before sending audio
                buffer = self._buffer_queue.get(timeout=.5)  # wait for buffer with timeout to avoid blocking indefinitely
                if buffer:
                    self._mic_device.write_frames(buffer)
            except queue.Empty:
                print("Buffer queue is empty, continuing...")
                continue

def main():

    # set api_key
    # Get it from the website under python.
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
    # FYI : don't use "-" in a username, use an "_"
    meeting = birdconv.create_token( room , "Delay_Audio") 
    print("Meeting URL: "   + meeting["url"])
    # print("Meeting Token: " + meeting["token"])

    print("sleeping for 1 second")
    time.sleep(1)

    Daily.init()

    app = AudioApp(SAMPLE_RATE, NUM_CHANNELS)

    try: 
        app.run(meeting)
    except KeyboardInterrupt:
        print("Ctrl-C detected. Exiting!")
    finally:
        app.leave()


if __name__ == '__main__':
    main()
