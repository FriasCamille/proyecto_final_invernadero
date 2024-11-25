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

# Nueva variable global para almacenar la temperatura personalizada
custom_setpoint = None
stop_event = threading.Event()  # Evento para detener hilos cuando sea necesario


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


def solve_temp_loop():
    """
    Bucle continuo para ajustar la temperatura en base al setpoint actual.
    """
    while not stop_event.is_set():
        setpoint = get_setpoint()
        actual_temp = read_temperature()
        if actual_temp < setpoint - 1:  # Por debajo del rango
            power = 20
        elif actual_temp > setpoint + 1:  # Por encima del rango
            power = 100
        else:  # Dentro del rango
            power = 20

        # Aplicar potencia a los motores
        set_motor_power(pwm_motor_1, power)
        set_motor_power(pwm_motor_2, power)
        time.sleep(1)


def solve_humidity_loop():
    """
    Bucle continuo para gestionar la humedad.
    """
    while not stop_event.is_set():
        if GPIO.input(PIN_INTERRUPT) == GPIO.HIGH:
            GPIO.output(PIN_OUTPUT, GPIO.HIGH)
            print("Interrupción detectada, PIN 16 en ALTO")
        else:
            GPIO.output(PIN_OUTPUT, GPIO.LOW)
        time.sleep(1)


def start_loops():
    """
    Inicia los hilos para temperatura y humedad.
    """
    stop_event.clear()  # Asegura que los hilos no estén detenidos
    threading.Thread(target=solve_temp_loop, daemon=True).start()
    threading.Thread(target=solve_humidity_loop, daemon=True).start()


def stop_loops():
    """
    Detiene los hilos de temperatura y humedad.
    """
    stop_event.set()


def main():
    """
    Inicia el control PID y los bucles de temperatura y humedad.
    """
    start_loops()
    try:
        while True:
            setpoint = get_setpoint()
            control_temperature(setpoint)  # PID
            time.sleep(5)  # Ajustar según la necesidad
    except KeyboardInterrupt:
        stop_loops()
        cleanup()


if __name__ == "__main__":
    main()
