import numpy as np
import sounddevice as sd

def generate_tone(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.5 * np.sin(2 * np.pi * frequency * t)
    return waveform

def play_tone(waveform, sample_rate=44100):
    sd.play(waveform, samplerate=sample_rate)
    sd.wait()

# Example usage

def main() :
    frequency = 440.0  # A4
    duration = 1.0     # 1 second

    waveform = generate_tone(frequency, duration)
    play_tone(waveform)


if __name__ == '__main__':
    main()