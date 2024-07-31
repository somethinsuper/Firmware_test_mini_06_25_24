import numpy as np
import matplotlib
import serial

print("test")
ser = serial.Serial('/dev/cu.usbserial-1440', 9600, 
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
    )
s = ser.isOpen()
print(s) 

while True:
    data = ser.readline().decode().strip()
    if data:
        print(data)
        

