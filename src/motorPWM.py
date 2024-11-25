import RPi.GPIO as GPIO
import time
from threading import Lock

GPIO.setwarnings(False)  # Deshabilita advertencias previas
GPIO.setmode(GPIO.BCM)

motor_lock = Lock()  # Bloqueo para evitar accesos concurrentes

def setup_motor(pin, frequency=250):
    """
    Configura el pin como salida PWM para controlar el motor.

    Args:
        pin: Pin GPIO conectado al motor.
        frequency: Frecuencia del PWM (en Hz).

    Returns:
        pwm: Objeto PWM inicializado.
    """
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, frequency)
    pwm.start(0)
    return pwm


def set_motor_power(pwm, power):
    """
    Ajusta la potencia del motor.

    Args:
        pwm: Objeto PWM configurado.
        power: Potencia en porcentaje (0-100).
    """
    with motor_lock:  # Asegura que solo un proceso acceda al PWM
        if validate_power(power):
            pwm.ChangeDutyCycle(power)
            print(f"Potencia del motor ajustada a: {power}%")
        else:
            print("Error: La potencia debe estar entre 0 y 100.")


def validate_power(power):
    """
    Valida si la potencia está en el rango permitido.

    Args:
        power: Potencia a validar.

    Returns:
        bool: True si es válida, False de lo contrario.
    """
    return 0 <= power <= 100


def cleanup():
    """
    Limpia los pines GPIO.
    """
    GPIO.cleanup()


def example_motor_control():
    """
    Ejemplo de control dinámico del motor en un bucle.
    """
    motor_pin = 20  # Pin GPIO conectado al motor
    pwm_motor = setup_motor(motor_pin, frequency=250)

    try:
        while True:
            potencia = float(input("Introduce la potencia del motor (0-100): "))
            if validate_power(potencia):
                set_motor_power(pwm_motor, potencia)
            else:
                print("Por favor, introduce un valor entre 0 y 100.")
    except KeyboardInterrupt:
        print("Control del motor detenido por el usuario.")
    finally:
        cleanup()


if __name__ == "__main__":
    example_motor_control()
