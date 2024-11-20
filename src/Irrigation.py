import RPi.GPIO as GPIO
import time
import Temperature

fan_1 = 16
fan_2 = 17
water_pump = 18 

MAX_TEMP = 30

WATERING_TIME = 50

GPIO.setup(fan_1, GPIO.OUT)
GPIO.setup(fan_2, GPIO.OUT)
GPIO.setup(water_pump, GPIO.OUT)

def Humidity():
     // Función que lee la humedad o determina el ciclo de regado
    return True

while True:

    while Temperature.Temperature() > MAX_TEMP:
        GPIO.setup(fan_1, GPIO.HIGH)
        GPIO.setup(fan_2, GPIO.HIGH)
        
        
    GPIO.setup(fan_1, GPIO.LOW)
    GPIO.setup(fan_2, GPIO.LOW)
    
    if Humidity() == True:
        GPIO.setup(water_pump, GPIO.HIGH)
        time.sleep(WATERING_TIME)
        GPIO.setup(water_pump, GPIO.LOW)
