import serial
import serial.tools.list_ports
import time

# Find STM32 COM port
devices = serial.tools.list_ports.comports()
STM_device = None
for device in devices:
    if "STMicroelectronics STLink Virtual COM Port" in device.description:
        STM_device = device.device

if STM_device is None:
    raise Exception("STM32 device not found.")

ser = serial.Serial(STM_device, baudrate=921600, bytesize=8, parity="N", stopbits=1)

print(f"Connected to: {STM_device}")

# Open the binary file to write the raw ADC values
file_1 = open("raw_ADC_values.data", "wb")
x = ser.read(500000) #Read 500000 bytes over UART
file_1.write(x)
file_1.close()
ser.close()