'import read_serial'
import serial
import serial.tools.list_ports
import wave
import time
import numpy as np
import matplotlib.pyplot as plt
import csv as csv_module  # Avoid naming conflict with csv()

SAMPLING_FREQUENCY = 20000

devices = serial.tools.list_ports.comports()
STM_device = None
for device in devices:
    if "STMicroelectronics STLink Virtual COM Port" in device.description:
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
        byte_size = record_duration*SAMPLING_FREQUENCY*2 #calculate byte size
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
                data = ser.read_until(expected="\n", size=2000000)  # Read data in chunks of 1024 bytes
                #until fully filled or encounter timeout
                if data:
                    file.write(data)
                    file.flush()
                    wav()
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
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        
        if sample_width == 2:
            data = np.frombuffer(signal, dtype=np.int16)
        else:
            raise ValueError("Unsupported sample width")

        if num_channels == 2:
            data = data[::2]  # Use one channel if stereo

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
        plt.savefig('waveform' + time_date + '.png', dpi=300)
        plt.close()

    print("PNG generated\n")

def wav():
    'generate wav file'
    global wav_file # wav_file, made global to use in csv and png file name
    global time_date # time and date at recording, made global to use in wav, csv and png file name

    time_date = time.strftime("%Y-%m-%d %I-%M-%S-%p")
    wav_file = "test audio at " + time_date +".wav"
    print (wav_file)

    print("WAV generated")

if __name__ == '__main__':
    main()
