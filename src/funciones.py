
import threading
import RPi.GPIO as GPIO
import time
from motorPWM import setup_motor, set_motor_power, cleanup
from Temperature import read_temperature
from PID import control_temperature

# Configuración de GPIO
PIN_MOTOR_1 = 20
PIN_MOTOR_2 = 21
PIN_INTERRUPT = 26
PIN_OUTPUT = 16

# Limpieza inicial para evitar conflictos
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_OUTPUT, GPIO.OUT)

# Configuración de motores
pwm_motor_1 = setup_motor(PIN_MOTOR_1)
pwm_motor_2 = setup_motor(PIN_MOTOR_2)

def get_setpoint():
    """
    Determina la temperatura deseada (setpoint) basada en la hora actual.

    :return: Temperatura deseada (float).
    """
    current_hour = time.localtime().tm_hour
    if 6 <= current_hour < 20:  # De 6:00 AM a 8:00 PM
        return 25.0  # Punto medio entre 21 y 29
    else:  # De 8:00 PM a 6:00 AM
        return 12.5  # Punto medio entre 10 y 15

def solve_temp(setpoint):
    actual_temp=read_temperature()
    if actual_temp < setpoint - 1:  # Por debajo del rango
        power = 20
    elif actual_temp > setpoint + 1:  # Por encima del rango
        power = 100
    else:  # Dentro del rango
        power = 20

    # Aplicar potencia a los motores
    set_motor_power(pwm_motor_1, power)
    set_motor_power(pwm_motor_2, power)

def solve_humidity():
    if GPIO.input(PIN_INTERRUPT) == GPIO.HIGH:
        GPIO.output(PIN_OUTPUT, GPIO.HIGH)
        print("Interrupción detectada, PIN 16 en ALTO")
        time.sleep(1)
        GPIO.output(PIN_OUTPUT, GPIO.LOW)
    else:
        GPIO.output(PIN_OUTPUT, GPIO.LOW)


def main():
    """
    Ejecuta el control PID ajustando automáticamente el setpoint según la hora.
    """
    while True:
        setpoint = get_setpoint()  # Obtén el setpoint dinámicamente
        control_temperature(setpoint)  # Llama a la función de control de temperatura
        solve_temp(setpoint)
        solve_humidity()
if _name_ == "_main_":
    main()