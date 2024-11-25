from machine import Pin, ADC
import time


sensor_pin = ADC(Pin(26))  
output_pin = Pin(14, Pin.OUT) 


def calcular_porcentaje_humedad(valor):

    valor_min = 65000  
    valor_max = 30000  


    humedad = ((valor - valor_min) / (valor_max - valor_min)) * 100


    humedad = max(0, min(100, humedad))
    return humedad


def controlar_humedad(humedad, pin, min_humedad=10, max_humedad=30):
    if humedad < min_humedad:  
        pin.value(1)  
        print("Humedad baja. Activando salida...")
    elif humedad > max_humedad:  
        pin.value(0)  
        print("Humedad alta. Desactivando salida...")
    else:
        print("Humedad dentro del rango adecuado.")
        pin.value(0)
        
def humedad():
    
    valor_humedad = sensor_pin.read_u16()
    
    porcentaje_humedad = calcular_porcentaje_humedad(valor_humedad)
    
    controlar_humedad(porcentaje_humedad, output_pin)

    time.sleep(1)


