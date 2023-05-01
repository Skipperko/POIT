import serial 
import time

def main_func():
    list_of_floats = []
    list_values = []
    
    arduino = serial.Serial('/dev/cu.usbmodem143101', 9600)
    arduino_data = arduino.readline()
    
    decoded_values = str(arduino_data[0:len(arduino_data)].decode('utf-8'))
    
    list_values = decoded_values.split('x')
    
    for item in list_values:
        list_of_floats.append(float(item))
        
    print('Collected data: ', list_of_floats[2])
    
    arduino_data = 0
    list_of_floats.clear()
    arduino.close()
    
def main():
    while True:
        main_func()
        
main()