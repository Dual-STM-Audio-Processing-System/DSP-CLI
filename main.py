import serial
import serial.tools.list_ports
import wave
import time
import numpy as np
import matplotlib.pyplot as plt
import csv as csv_module  # Avoid naming conflict with csv()
import subprocess

SAMPLING_FREQUENCY = 20000
BITS_PER_SAMPLE = 8
GAIN = 2

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
                break
            else:
                print("Error invalid option\n")
        except ValueError:
            print("Error: Only numbers are accepted\n")

def manual_recording():
    ser = serial.Serial(STM_device, baudrate=921600, bytesize=8, parity="N", stopbits=1)
    with open("raw_ADC_values.data", "wb") as file:
        data = 0
        record_duration = int(input("Recording Duration (s): "))
        byte_size = record_duration*SAMPLING_FREQUENCY*1 #calculate byte size
        print("Recording in progress\n")
        data = ser.read(byte_size)
        file.write(data)
        file.flush()
    'once data written into file generate all csv,png and wav'
    wav()
    csv()
    png()
    with open("raw_ADC_values.data", "wb") as file:
        file.truncate(0)
        file.seek(0)
    ser.close()
    return
def ultrasonic_recording():
    recording_distance = int(input("Recording Distance (cm): "))
    ser = serial.Serial(STM_device, baudrate=921600, bytesize=8, parity="N", stopbits=1, inter_byte_timeout=0.5)
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
                    csv()
                    png()
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
def csv():
    with wave.open(wav_file, 'rb') as wf:
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

        with open('output' + time_date +'.csv', 'w', newline='') as file:
            writer = csv_module.writer(file)
            writer.writerow(['Time (s)', 'Amplitude'])
            for t, amp in zip(time_axis, data):
                writer.writerow([t, amp])

    print("CSV generated")

def png():
    with wave.open(wav_file, 'rb') as wf:
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
        plt.savefig('waveform' + time_date + '.png', dpi=300)
        plt.close()

    print("PNG generated\n")

def wav():
    global wav_file # wav_file, made global to use in csv and png file name
    global time_date # time and date at recording, made global to use in wav, csv and png file name

    time_date = time.strftime("%Y-%m-%d %I-%M-%S-%p")
    wav_file = time_date +".wav"

    result = subprocess.run(["WavFileConverter.exe", "raw_ADC_values.data", wav_file, str(SAMPLING_FREQUENCY), str(BITS_PER_SAMPLE), str(GAIN)], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: WavFileConverter.exe failed to run successfully.")
        return 1

    print("WAV generated")
    return 0

if __name__ == '__main__':
    main()
