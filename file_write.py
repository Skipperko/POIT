import os

def write_to_file(data):
    file = open("data/data.csv", "a")
    
    if os.stat('data/data.csv').st_size == 0:
        file.write("Humidity, Temperature, Distance\n")
        
    line = "{},{},{}\n".format(data[0], data[1], data[2])
    file.write(line)
    
    return