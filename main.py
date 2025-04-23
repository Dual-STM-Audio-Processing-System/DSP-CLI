'import read_serial'
import time
import math
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

def ultrasonic_recording():
    while True:
        try:
            'record distance from ultrasonic?'
            'receieve transmission while distance <=10'
            print("transmitting")
            time.sleep(1)
            'once distance >10 for specific amount of time generate all csv,png and wav'
        except KeyboardInterrupt:
            main()
        
def csv():
    'generate csv'

def png():
    'generate png'

def wav():
    'generate wav file'

if __name__ == '__main__':
    main()
