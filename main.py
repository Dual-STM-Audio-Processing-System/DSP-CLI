import read_serial

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
    elif choice == 2:
        'Function to UART2 signal to processing stm to be in distance recording'
        print("In distance recording mode")

if __name__ == '__main__':
    main()
