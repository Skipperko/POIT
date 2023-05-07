import csv
def read_file():
    with open('data/data.csv', 'r') as data:
        reader = csv.reader(data)
        index = 1
        id = []
        humidity = []
        temperature = []

        for row in reader:
            if index > 1:
                id.append(index)
                humidity.append(float(row[0]))
                temperature.append(float(row[1]))
            index +=1
            
    return [id[1:], humidity[1:], temperature[1:]]