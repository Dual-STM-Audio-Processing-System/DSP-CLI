import read_serial
import time

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
        'Function to send UART2 signal to processing stm to be in manual recording and duration of recording'
        print("In manual recording mode") 
        manual_recording()
    elif choice == 2:
        'Function to UART2 signal to processing stm to be in distance recording'
        print("In distance recording mode")
        ultrasonic_recording()

def manual_recording():
    record_duration = int(input("Recording Duration (s): "))
    start_time = time.time
    current_time = time.time
    while (current_time-start_time)<record_duration:
        current_time = time.time
        'receive transmission'
    'once out of loop generate all csv,png and wav'

def ultrasonic_recording():
    while True:
        'record distance from ultrasonic?'
        'receieve transmission'
        'once distance >10 for specific amount of time generate all csv,png and wav'
        
def csv():
    'generate csv'

def png():
    'generate png'

def wav():
    'generate wav file'
    
if __name__ == '__main__':
    main()
