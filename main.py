import sys
import serial
import serial.tools.list_ports
import wave
import time
import numpy as np
import matplotlib.pyplot as plt
import csv as csv_module  # Avoid naming conflict with csv()
import subprocess
import os
from scipy.fft import fft, fftfreq

SAMPLING_FREQUENCY = 20000
BITS_PER_SAMPLE = 8
GAIN = 1
BYTES_PER_SAMPLE = 1

devices = serial.tools.list_ports.comports()
STM_device = None
for device in devices:
    if "STMicroelectronics STLink Virtual COM Port (COM6)" in device.description:
        STM_device = device.device

if STM_device is None:
    raise Exception("STM32 device not found.")

print(f"Connected to: {STM_device}")

def main():
    while True:
        choice = -1
        print("Main Menu")
        print("-------------------------")
        print("1: Manual Recording Mode")
        print("2: Distance Recording Mode")
        print("3: Exit")
        try:
            choice = int(input("Option: "))
            if choice == 1:
                print("In manual recording mode\n")
                manual_recording()
            elif choice == 2:
                print("In distance recording mode\n")
                ultrasonic_recording()
            elif choice == 3:
                sys.exit(0)
            else:
                print("Error invalid option\n")
        except ValueError:
            print("Error: Only numbers are accepted\n")

def manual_recording():
    ser = serial.Serial(STM_device, baudrate=921600, bytesize=8, parity="N", stopbits=1)
    with open("raw_ADC_values.data", "wb") as file:
        data = 0
        record_duration = int(input("Recording Duration (s): "))
        byte_size = record_duration*SAMPLING_FREQUENCY*BYTES_PER_SAMPLE #calculate byte size
        print("Recording in progress\n")
        data = ser.read(byte_size)
        file.write(data)
        print(f"Bytes written: {len(data)}")
        file.flush()
    #once data written into file generate wav file, then let user decide other output formats
    ret = wav()
    if ret != 0:
        ser.write(f"2U".encode('utf-8'))
        ser.close()
        print("Something went wrong lol")
        return
    generate_artefacts()
    with open("raw_ADC_values.data", "wb") as file:
        file.truncate(0)
        file.seek(0)
    ser.close()
    return

def ultrasonic_recording():
    recording_distance = int(input("Recording Distance (cm): "))
    ser = serial.Serial(STM_device, baudrate=921600, bytesize=8, parity="N", stopbits=1, inter_byte_timeout=0.5) #timeout after 500ms of not receiving data
    ser.write(f"1U {recording_distance}".encode('utf-8'))
    with open("raw_ADC_values.data", "wb") as file:
        while True:
            print("Recording in progress\n")
            try:
                data = ser.read_until(expected=b"cums", size=2000000)  # Read data in chunks of 1024 bytes
                #until fully filled or encounter timeout
                if data:
                    file.write(data)
                    file.flush()
                    ret = wav()
                    if ret != 0:
                        ser.write(f"2U".encode('utf-8'))
                        ser.close()
                        return
                    generate_artefacts()
                    file.truncate(0)
                    file.seek(0)
                else:
                    continue            
            except KeyboardInterrupt:
                ser.write(f"2U".encode('utf-8'))
                ser.close()
                print("Recording stopped")
                break
    print('\n')
    return

def generate_artefacts():
    while True:
        choice = -1
        print("Artefact Generation Menu")
        print("-------------------------")
        print("1: CSV Generation")
        print("2: PNG Generation")
        print("3: DFT Generation")
        print("4: Exit")
        try:
            choice = int(input("Option: "))
            if choice == 1:
                csv()
            elif choice == 2:
                png()
            elif choice == 3:
                dft()
            elif choice == 4:
                print()
                return
            else:
                print("Error invalid option\n")
        except ValueError:
            print("Error: Only numbers are accepted\n")

def csv():
    with wave.open(folder_path + "\\" + wav_file, 'rb') as wf:
        n_frames = wf.getnframes()
        framerate = wf.getframerate()
        signal = wf.readframes(n_frames)
        sample_width = wf.getsampwidth()

        if sample_width == 2:
            data = np.frombuffer(signal, dtype=np.int16)
        elif sample_width == 1:
            raw = np.frombuffer(signal, dtype=np.uint8)
            data = raw.astype(np.int16) - 128  # Center around 0
        else:
            raise ValueError("Unsupported sample width")


        time_axis = np.linspace(0, len(data) / framerate, num=len(data))

        with open(folder_path + '\\' + 'CSV output at ' + time_date + ', Team 02, Sampling Frequency ' + str(SAMPLING_FREQUENCY) + 'Hz' + '.csv', 'w', newline='') as file:
            writer = csv_module.writer(file)
            writer.writerow(['Time (s)', 'Amplitude'])
            for t, amp in zip(time_axis, data):
                writer.writerow([t, amp])

    print("CSV generated\n")

def png():
    with wave.open(folder_path + "\\" + wav_file, 'rb') as wf:
        n_frames = wf.getnframes()
        framerate = wf.getframerate()
        signal = wf.readframes(n_frames)
        sample_width = wf.getsampwidth()

        if sample_width == 2:
            data = np.frombuffer(signal, dtype=np.int16)
        elif sample_width == 1:
            raw = np.frombuffer(signal, dtype=np.uint8)
            data = raw.astype(np.int16) - 128  # Center around 0
        else:
            raise ValueError("Unsupported sample width")

        time_axis = np.linspace(0, len(data) / framerate, num=len(data))

        plt.figure(figsize=(10, 4))
        plt.plot(time_axis, data)
        plt.title('Waveform')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.tight_layout()
        plt.savefig(folder_path + "\\" + 'Amplitude vs Time Waveform at ' + time_date + ', Team 02, Sampling Frequency ' + str(SAMPLING_FREQUENCY) + 'Hz' + '.png', dpi=300)
        plt.close()

    print("PNG generated\n")

def wav():
    global wav_file # wav_file, made global to use in csv and png file name
    global time_date # time and date at recording, made global to use in wav, csv and png file name
    global folder_path 
    time_date = time.strftime("%d-%m-%Y %I-%M-%S-%p")
    wav_file = time_date + "-Team-02-Sampling Frequency " + str(SAMPLING_FREQUENCY) + 'Hz' + ".wav"
    folder_path = "Recording data at " + time_date

    try:
        os.mkdir(folder_path)
        print(f"Folder '{folder_path}' created successfully.")

    except FileExistsError:
        print(f"Folder '{folder_path}' already exists.")

    except FileNotFoundError:
        print(f"Parent directory not found for '{folder_path}'.")
    
    result = subprocess.run(["WavFileConverter.exe", "raw_ADC_values.data", folder_path + "\\" + wav_file, str(SAMPLING_FREQUENCY), str(BITS_PER_SAMPLE), str(GAIN)], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: WavFileConverter.exe failed to run successfully.")
        return 1

    print("WAV generated\n")
    return 0

def dft():
    with wave.open(folder_path + "\\" + wav_file, 'rb') as wf:
        n_frames = wf.getnframes()
        framerate = wf.getframerate()
        signal = wf.readframes(n_frames)
        sample_width = wf.getsampwidth()

        if sample_width == 2:
            data = np.frombuffer(signal, dtype=np.int16)
        elif sample_width == 1:
            raw = np.frombuffer(signal, dtype=np.uint8)
            data = raw.astype(np.int16) - 128  # Center around 0
        else:
            raise ValueError("Unsupported sample width")

        # Perform FFT
        N = len(data)
        yf = fft(data)
        xf = fftfreq(N, 1 / framerate)

        # Only plot the positive half of the spectrum
        idx = np.where(xf >= 0)
        xf = xf[idx]
        yf = np.abs(yf[idx])

        # Plot FFT
        plt.figure(figsize=(10, 4))
        plt.plot(xf, yf)
        plt.title('FFT Spectrum')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.tight_layout()
        plt.savefig(folder_path + '\\' + 'fft_' + time_date + ', Team 02, Sampling Frequency ' + str(SAMPLING_FREQUENCY) + 'Hz' + '.png', dpi=300)
        plt.close()

    print("DFT PNG generated\n")

if __name__ == '__main__':
    main()
