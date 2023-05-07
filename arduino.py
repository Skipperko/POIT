import serial 
import time

def get_data():
    data = []
    list_values = []
    
    arduino = serial.Serial('/dev/cu.usbmodem143101', 9600)
    arduino_data = arduino.readline()
    
    decoded_values = str(arduino_data[0:len(arduino_data)].decode('utf-8', errors='ignore'))
    
    list_values = decoded_values.split('x')
    
    for item in list_values:
        if item[0] == ".":
            fixed = item[1:]
            data.append(float(fixed))
        else:
            data.append(float(item))
        
    arduino.close()

    return data    
