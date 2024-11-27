import threading
import RPi.GPIO as GPIO
import time
import logging
from motorPWM import setup_motor, set_motor_power, cleanup
from Temperature import read_temperature
from PID import control_temperature, write_power
from funciones import ciclo, update_custom_setpoint

# Configuración del logging
logging.basicConfig(
    filename='function_calls.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

PIN_MOTOR_1 = 20
PIN_MOTOR_2 = 21
PIN_INTERRUPT = 26
PIN_OUTPUT = 16

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Configuración de motores
try:
    pwm_motor_1 = setup_motor(PIN_MOTOR_1)
    pwm_motor_2 = setup_motor(PIN_MOTOR_2)
    print("Motores inicializados correctamente.")
except Exception as e:
    print(f"Error al inicializar motores: {e}")
    pwm_motor_1 = pwm_motor_2 = None

def motor_derecho(potencia):
    if pwm_motor_1:
        logging.info(f'Función llamada: motor_derecho con potencia={potencia}')
        set_motor_power(pwm_motor_1, potencia)
    else:
        logging.error("pwm_motor_1 no inicializado.")

def motor_izquierdo(potencia):
    if pwm_motor_2:
        logging.info(f'Función llamada: motor_izquierdo con potencia={potencia}')
        set_motor_power(pwm_motor_2, potencia)
    else:
        logging.error("pwm_motor_2 no inicializado.")

def ambos_motore(potencia):
    if pwm_motor_1 and pwm_motor_2:
        logging.info(f'Función llamada: ambos_motore con potencia={potencia}')
        set_motor_power(pwm_motor_1, potencia)
        set_motor_power(pwm_motor_2, potencia)
    else:
        logging.error("Motores no inicializados.")

def bomba(senal):
    logging.info(f'Función llamada: bomba con senal={senal}')
    if senal == 1:
        GPIO.output(PIN_OUTPUT, GPIO.HIGH)
    else:
        GPIO.output(PIN_OUTPUT, GPIO.LOW)

def potencia_foco(potencia):
    logging.info(f'Función llamada: potencia_foco con potencia={potencia}')
    write_power(potencia)

def set_PID(temp):
    logging.info(f'Función llamada: set_PID con temp={temp}')
    control_temperature(temp)

def temperatura():
    logging.info('Función llamada: temperatura')
    return read_temperature()

def predeterminado():
    logging.info('Revirtiendo a ciclo de setpoint predeterminado')
    update_custom_setpoint(None)

def set_value(temp):
    if temp is not None and not (0 <= temp <= 100):
        logging.warning(f'Setpoint inválido: {temp}')
        raise ValueError("Setpoint debe estar entre 0 y 100.")
    update_custom_setpoint(temp)
