import RPi.GPIO as GPIO
import time
from threading import Lock

GPIO.setwarnings(False)  # Deshabilita advertencias previas
GPIO.setmode(GPIO.BCM)

motor_lock = Lock()  # Bloqueo para evitar accesos concurrentes

# Estados de los ventiladores
fan_states = {"fan1": False, "fan2": False}

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


def set_motor_power(pwm, power, fan):
    """
    Ajusta la potencia del motor si está encendido.

    Args:
        pwm: Objeto PWM configurado.
        power: Potencia en porcentaje (0-100).
        fan: Identificador del ventilador (fan1, fan2).
    """
    with motor_lock:
        if fan_states[fan]:  # Verifica si el ventilador está encendido
            if validate_power(power):
                pwm.ChangeDutyCycle(power)
                print(f"Potencia del {fan} ajustada a: {power}%")
            else:
                print("Error: La potencia debe estar entre 0 y 100.")
        else:
            print(f"El {fan} está apagado. No se puede ajustar la potencia.")


def toggle_fan(fan, state):
    """
    Enciende o apaga el ventilador.

    Args:
        fan: Identificador del ventilador (fan1, fan2).
        state: Estado deseado (True para encender, False para apagar).
    """
    with motor_lock:
        fan_states[fan] = state
        print(f"{fan} {'encendido' if state else 'apagado'}")


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


# Ejemplo de configuración para dos ventiladores
if __name__ == "__main__":
    motor1_pin = 20
    motor2_pin = 21
    try:
        pwm_motor1 = setup_motor(motor1_pin)
        pwm_motor2 = setup_motor(motor2_pin)

        # Encender y ajustar potencia de ejemplo
        toggle_fan("fan1", True)  # Enciende el ventilador 1
        set_motor_power(pwm_motor1, 50, "fan1")

        toggle_fan("fan2", True)  # Enciende el ventilador 2
        set_motor_power(pwm_motor2, 75, "fan2")

        # Apagar
        toggle_fan("fan1", False)  # Apaga el ventilador 1
        set_motor_power(pwm_motor1, 50, "fan1")  # No tendrá efecto

    except KeyboardInterrupt:
        print("Control del motor detenido por el usuario.")
    finally:
        cleanup()
