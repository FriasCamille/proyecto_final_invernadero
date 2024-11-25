import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)  

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
    if 0 <= power <= 100:
        pwm.ChangeDutyCycle(power)  
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
    motor_pin = 20  
    try:
        pwm_motor = setup_motor(motor_pin, frequency=250)  
        
        while True:
            potencia = get_motor_power_input()
            set_motor_power(pwm_motor, potencia)
            time.sleep(0.5)  
            
    except KeyboardInterrupt:
        print("Detenido por el usuario.")
    finally:
        cleanup()