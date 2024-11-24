import time


sensor_1 = '/sys/bus/w1/devices/28-fd58770e64ff/w1_slave'
sensor_2 = '/sys/bus/w1/devices/28-fd58770e64ff/w1_slave'
sensor_3 = '/sys/bus/w1/devices/28-fd58770e64ff/w1_slave'
sensor_4 = '/sys/bus/w1/devices/28-fd58770e64ff/w1_slave'

sensors=[sensor_1, sensor_2, sensor_3, sensor_4 ]

def sensor_temperature(sensor_file):
    try:
        with open(sensor_file, 'r') as file:
            lines = file.readlines()
        
        if lines[0].strip().endswith('YES'):
            temperature_data = lines[1].split("t=")
            if len(temperature_data) == 2:
                temperature_c = float(temperature_data[1]) / 1000.0
                return temperature_c
    except FileNotFoundError:
        return "Sensor no encontrado"
    except Exception as e:
        return f"Error: {e}"
    return "Lectura fallida"
    
def average(temperatures):
    sum =0 
    for i in temperatures:
        sum+=i
    return sum/len(temperatures)
    
def read_temperature():
    temps=[]
    for i in sensors:
        temp = sensor_temperature(i)
        if instance(temp,float):
            temps.append(temp)
    return average(temps)
    
read_temperature()
    
