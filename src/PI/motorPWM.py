import RPi.GPIO as GPIO

GPIO.setwarnings(False)  # Desactiva advertencias de GPIO
GPIO.cleanup()  # Limpia los recursos previos
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

def cleanup():
    """
    Limpia los pines GPIO.
    """
    GPIO.cleanup()
