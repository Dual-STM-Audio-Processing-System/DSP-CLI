'import read_serial'
import time
import math
import wave
import numpy as np
import matplotlib.pyplot as plt
import csv as csv_module  # Avoid naming conflict with csv()

def main():
    choice = -1
    print("Main Menu")
    print("-------------------------")
    print("1: Manual Recording Mode")
    print("2: Distance Recording Mode")
    while True:
        try:
            choice = int(input("Option: "))
            if choice == 1 or choice == 2:
                break
            else:
                print("Error invalid option")
        except ValueError:
            print("Error: Only numbers are accepted")
    if choice == 1:
        print("In manual recording mode") 
        manual_recording()
    elif choice == 2:
        print("In distance recording mode")
        ultrasonic_recording()

def manual_recording():
    data = 0
    record_duration = int(input("Recording Duration (s): "))
    start_time = time.time()
    current_time = 0
    recording_time = 0

    while (recording_time<record_duration):
        
        'receive transmission'
        print("receiving")
        time.sleep(1)
        current_time = time.time()
        recording_time = current_time-start_time
    'once out of loop generate all csv,png and wav'
    wav()
    csv()
    png()
    print('\n')
    main()
    
def ultrasonic_recording():
    while True:
        try:
            'record distance from ultrasonic?'
            'receieve transmission while distance <=10'
            print("transmitting")
            time.sleep(1)
            'once distance >10 for specific amount of time generate all csv,png and wav'
        except KeyboardInterrupt:
            print('')
            wav()
            csv()
            png()
            print('\n')
            main()

        
def csv():
    wav_file = 'test.wav'
    with wave.open(wav_file, 'rb') as wf:
        n_frames = wf.getnframes()
        framerate = wf.getframerate()
        signal = wf.readframes(n_frames)
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        
        if sample_width == 2:
            data = np.frombuffer(signal, dtype=np.int16)
        else:
            raise ValueError("Unsupported sample width")

        if num_channels == 2:
            data = data[::2]  # Use one channel if stereo

        time_axis = np.linspace(0, len(data) / framerate, num=len(data))

        with open('output.csv', 'w', newline='') as file:
            writer = csv_module.writer(file)
            writer.writerow(['Time (s)', 'Amplitude'])
            for t, amp in zip(time_axis, data):
                writer.writerow([t, amp])

    print("CSV generated")

def png():
    wav_file = 'test.wav'
    with wave.open(wav_file, 'rb') as wf:
        n_frames = wf.getnframes()
        framerate = wf.getframerate()
        signal = wf.readframes(n_frames)
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()

        if sample_width == 2:
            data = np.frombuffer(signal, dtype=np.int16)
        else:
            raise ValueError("Unsupported sample width")

        if num_channels == 2:
            data = data[::2]  # Use one channel if stereo

        time_axis = np.linspace(0, len(data) / framerate, num=len(data))

        plt.figure(figsize=(10, 4))
        plt.plot(time_axis, data)
        plt.title('Waveform')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.tight_layout()
        plt.savefig('waveform.png')
        plt.close()

    print("PNG generated")

def wav():
    'generate wav file'
    print("WAV generated")

if __name__ == '__main__':
    main()
