from machine import Pin, ADC
import time

# Configuración de pines
sensor_pin = ADC(Pin(26))  # Pin ADC (lectura del sensor)
output_pin = Pin(14, Pin.OUT)  # Pin de salida para la señal

# Función para calcular el porcentaje de humedad
def calcular_porcentaje_humedad(valor):
    # Valores mínimos y máximos ajustados según calibración
    valor_min = 65000  # Valor ADC en seco
    valor_max = 30000  # Valor ADC completamente sumergido (ajustar según pruebas)

    # Calcular la humedad proporcionalmente
    humedad = ((valor - valor_min) / (valor_max - valor_min)) * 100

    # Limitar el porcentaje al rango 0% - 100%
    humedad = max(0, min(100, humedad))
    return humedad

# Función para monitorear humedad y controlar el pin
def controlar_humedad(humedad, pin, min_humedad=10, max_humedad=30):
    if humedad < min_humedad:  # Si está por debajo del mínimo
        pin.value(1)  # Activa el pin (por ejemplo, sistema de riego)
        print("Humedad baja. Activando salida...")
    elif humedad > max_humedad:  # Si está por encima del máximo
        pin.value(0)  # Desactiva el pin
        print("Humedad alta. Desactivando salida...")
    else:
        print("Humedad dentro del rango adecuado.")
        pin.value(0)  # 
# Bucle principal
while True:
    # Leer el valor del sensor
    valor_humedad = sensor_pin.read_u16()

    # Calcular el porcentaje de humedad
    porcentaje_humedad = calcular_porcentaje_humedad(valor_humedad)

    # Mostrar el resultado
    print(f"Valor ADC: {valor_humedad}, Humedad: {porcentaje_humedad:.2f}%")

    # Monitorear la humedad y controlar el pin de salida
    controlar_humedad(porcentaje_humedad, output_pin)

    # Esperar un segundo antes de la siguiente lectura
    time.sleep(1)


