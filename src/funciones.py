
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

foco_pin = 18  # Cambia esto por el pin que uses para el foco
GPIO.setup(foco_pin, GPIO.OUT)
pwm_foco = GPIO.PWM(foco_pin, 250)  # Configurar PWM a 250 Hz
pwm_foco.start(0)  # Iniciar en 0% de potencia

# Limpieza inicial para evitar conflictos
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_OUTPUT, GPIO.OUT)

# Configuración de motores
pwm_motor_1 = setup_motor(PIN_MOTOR_1)
pwm_motor_2 = setup_motor(PIN_MOTOR_2)

# Nueva variable global para almacenar la temperatura personalizada
custom_setpoint = None

def encender_foco(potencia):
    """
    Enciende el foco con una potencia dada (0-100%).
    """
    set_motor_power(pwm_foco, potencia)
    print(f"Foco encendido con potencia: {potencia}%")

def apagar_foco():
    """
    Apaga el foco.
    """
    pwm_foco.ChangeDutyCycle(0)
    print("Foco apagado")

def get_setpoint():
    """
    Determina la temperatura deseada basada en la hora actual, 
    o utiliza el valor personalizado si está configurado.
    """
    global custom_setpoint
    if custom_setpoint is not None:
        return custom_setpoint  # Usar el valor personalizado si está definido

    current_hour = time.localtime().tm_hour
    if 6 <= current_hour < 20:  # De 6:00 AM a 8:00 PM
        return 25.0  # Temperatura diurna
    else:  # De 8:00 PM a 6:00 AM
        return 12.5  # Temperatura nocturna

def update_custom_setpoint(value):
    """
    Actualiza el setpoint personalizado desde la página web.
    """
    global custom_setpoint
    custom_setpoint = value


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
    else:
        GPIO.output(PIN_OUTPUT, GPIO.LOW)

def encender_motor(motor):
    """
    Enciende un motor específico.
    Args:
        motor: PWM del motor a encender.
    """
    set_motor_power(motor, 100)  # Encender al 100% de potencia
    print("Motor encendido")

def apagar_motor(motor):
    """
    Apaga un motor específico.
    Args:
        motor: PWM del motor a apagar.
    """
    set_motor_power(motor, 0)  # Apagar configurando potencia a 0
    print("Motor apagado")

def encender_ambos_motores():
    """
    Enciende ambos motores al 100% de potencia.
    """
    set_motor_power(pwm_motor_1, 100)
    set_motor_power(pwm_motor_2, 100)
    print("Ambos motores encendidos al 100%")

def apagar_ambos_motores():
    """
    Apaga ambos motores configurando su potencia a 0.
    """
    set_motor_power(pwm_motor_1, 0)
    set_motor_power(pwm_motor_2, 0)
    print("Ambos motores apagados")

def ajustar_potencia_motor(motor, potencia):
    """
    Ajusta la potencia de un motor específico.
    Args:
        motor: PWM del motor a ajustar.
        potencia: Potencia deseada en porcentaje (0-100).
    """
    set_motor_power(motor, potencia)
    print(f"Potencia del motor ajustada a {potencia}%")

def ajustar_potencia_ambos_motores(potencia):
    """
    Ajusta la potencia de ambos motores al mismo tiempo.
    Args:
        potencia: Potencia deseada en porcentaje (0-100).
    """
    set_motor_power(pwm_motor_1, potencia)
    set_motor_power(pwm_motor_2, potencia)
    print(f"Potencia de ambos motores ajustada a {potencia}%")



def main():
    """
    Ejecuta el control PID ajustando automáticamente el setpoint según la hora.
    """
    while True:
        setpoint = get_setpoint()  # Obtén el setpoint dinámicamente
        control_temperature(setpoint)  # Llama a la función de control de temperatura
        solve_temp(setpoint)
        solve_humidity()
if __name__ == "__main__":
    main()
