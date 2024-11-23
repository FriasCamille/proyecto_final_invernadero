# raspberry-control.py
import smbus2
import struct
import threading
import time
import math

# Dirección I2C del RP2040
SLAVE_ADDR = 0x0A  # Dirección del dispositivo esclavo RP2040
i2c = smbus2.SMBus(1)

# Función para escribir el valor de potencia en el esclavo I2C
def writePower(pwr):
    try:
        data = struct.pack('<f', pwr)  # Empaqueta el número como float
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
        i2c.i2c_rdwr(msg)  # Envía el mensaje
    except Exception as e:
        print(f"Error en la escritura I2C: {e}")

# Función para calcular y mostrar la potencia real basada en el ángulo de disparo
def calculate_real_power(brightness):
    if brightness == 0:
        return 100.0
    else:
        alpha = math.acos(1 - 2 * (brightness / 100))  # Aproximación del ángulo de disparo
        real_power = (1 - (alpha / math.pi) + (math.sin(2 * alpha) / (2 * math.pi))) * 100
        return real_power

# Hilo para solicitar potencia desde la consola y enviarla al RP2040
def control_thread():
    while True:
        try:
            
            power = float(input("Introduce la potencia (0-100): "))
            if 0 <= power <= 100:
                writePower(power)  # Envía el valor de potencia al RP2040
                
                # Calcula la potencia real basada en el valor enviado
                real_power = 100-calculate_real_power(power)
                
                # Muestra la potencia deseada y la potencia real calculada
                print(f"Potencia establecida en: {power}% | Potencia real aproximada: {real_power:.2f}%")
            else:
                print("Valor fuera de rango. Introduce un valor entre 0 y 100.")
        except ValueError:
            print("Entrada no válida. Introduce un número entre 0 y 100.")

# Inicia el hilo para el control de potencia
thread = threading.Thread(target=control_thread)
thread.start()

