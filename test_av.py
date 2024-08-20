import tkinter as tk
import time
import threading
# import subprocess
import birdconv
import numpy as np
import sounddevice as sd

class Stopwatch:
    def __init__(self, root):


        self.generate_tone()
        self.root = root
        self.root.title("Stopwatch")

        # Make the window almost full screen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')

        # Create a large label for the stopwatch time
        self.time_label = tk.Label(root, text="00:00:00.00", font=("Helvetica", 150), fg='white', bg='black')
        self.time_label.pack(expand=True)

        self.start_time = None
        self.running = False

        self.last_second = -1 

        # Start the update loop
        self.update_time()

    def start(self):
        self.start_time = time.time()
        self.running = True

    def stop(self):
        self.running = False

    def update_time(self):
        if self.running:
            elapsed_time = time.time() - self.start_time
            formatted_time = self.format_time(elapsed_time)
            self.time_label.config(text=formatted_time)
            
            # Get the current second
            current_second = int(elapsed_time)
            
            # Check if we've moved to a new second and if it's a multiple of 5
            if current_second != self.last_second and current_second % 5 == 0:
                threading.Thread(target=self.play_beep).start()
            
            # Update the last checked second
            self.last_second = current_second    
        
        self.root.after(5, self.update_time)  # Update every 10 milliseconds (hundredths)


    def generate_tone(self,frequency=440.0, duration=1.0, sample_rate=44100):
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        self.waveform = 0.5 * np.sin(2 * np.pi * frequency * t)

    def play_beep(self,sample_rate=44100):
        sd.play(self.waveform, samplerate=sample_rate)
        sd.wait()

    # def play_beep(self):
    #     try:
    #         # Play the sound using subprocess with Popen to make it non-blocking
    #         subprocess.Popen(['afplay', '/System/Library/Sounds/Funk.aiff'])
    #     except Exception as e:
    #         print(f"Failed to play beep sound: {e}")

    @staticmethod
    def format_time(seconds):
        hundredths = int((seconds - int(seconds)) * 100)
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}.{hundredths:02}"

def main():

    # set api_key
    birdconv.api_request["uid"] = "0dtTMNNV6tYiNoSco8fdL3lzyYp2"

    # get the list of birdconv devices
    devices  = birdconv.active()

    # pick the devices that you want to place in a call
    my_devices = []
    for device in devices :
        print( device["username"])     
        if device["username"] == "Alistair" or device["username"] == "Susi" or device["username"] == "Finn" :
            my_devices.append(device)
    
    # place 1 or more selected devices on a call
    room  = birdconv.create_room( my_devices, recording=True ) 


    root = tk.Tk()
    stopwatch = Stopwatch(root)

    # Start the stopwatch
    stopwatch.start()

    # Set up the close event
    root.protocol("WM_DELETE_WINDOW", stopwatch.stop)
    
    root.mainloop()

if __name__ == "__main__":
    main()