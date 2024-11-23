import RPi.GPIO as GPIO
import time

# Configuración del modo de numeración de pines
GPIO.setmode(GPIO.BCM)  # Usa numeración BCM (pines GPIO)

def setup_motor(pin, frequency=5000):
    """
    Configura el pin como salida PWM para controlar el motor.

    Args:
        pin: Pin GPIO conectado al motor.
        frequency: Frecuencia del PWM (en Hz).
    
    Returns:
        pwm: Objeto PWM inicializado.
    """
    GPIO.setup(pin, GPIO.OUT)  # Configura el pin como salida
    pwm = GPIO.PWM(pin, frequency)  # Inicia PWM con la frecuencia especificada
    pwm.start(0)  # Comienza con potencia 0%
    return pwm

def set_motor_power(pwm, power):
    """
    Ajusta la potencia del motor.
    
    Args:
        pwm: Objeto PWM configurado.
        power: Potencia en porcentaje (0-100).
    """
    if 0 <= power <= 100:
        pwm.ChangeDutyCycle(power)  # Cambia el ciclo de trabajo al valor especificado
    else:
        print("Error: La potencia debe estar entre 0 y 100.")

def get_motor_power_input():
    """
    Solicita al usuario un valor válido para la potencia del motor.

    Returns:
        float: Potencia en porcentaje (0-100).
    """
    while True:
        try:
            potencia = float(input("Introduce la potencia del motor (0-100): "))
            if 0 <= potencia <= 100:
                return potencia
            else:
                print("Por favor, introduce un valor entre 0 y 100.")
        except ValueError:
            print("Entrada no válida. Introduce un número válido entre 0 y 100.")

def cleanup():
    """
    Limpia los pines GPIO.
    """
    GPIO.cleanup()

# Ejemplo de uso
if __name__ == "__main__":
    motor_pin = 20  # Pin GPIO principal
    try:
        # Cambia la frecuencia según sea necesario (prueba con 5000 o 10000 Hz)
        pwm_motor = setup_motor(motor_pin, frequency=5000)  
        
        while True:
            potencia = get_motor_power_input()
            set_motor_power(pwm_motor, potencia)
            time.sleep(0.5)  # Pausa para observar los cambios
            
    except KeyboardInterrupt:
        print("Detenido por el usuario.")
    finally:
        cleanup()