import json

def parse_data(data):
    data = str(data)
    data = data[6:len(data)-4].replace("'", "\"")
    data = json.loads(data)
    id = []
    humidity = []
    temperature = []
    
    
    
    for element in data:
        id.append(element['id']) 
        humidity.append(element['Humidity'])
        temperature.append(element['Temperature']) 
        
    return [id, humidity, temperature]