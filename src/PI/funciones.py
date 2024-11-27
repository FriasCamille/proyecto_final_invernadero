import threading
import RPi.GPIO as GPIO
import time
from motorPWM import setup_motor, set_motor_power
from Temperature import read_temperature
from PID import control_temperature, PIDController

pid_controller = PIDController(kp=3.0, ki=2.5, kd=1.5)

# Configuración de GPIO
PIN_MOTOR_1 = 20
PIN_MOTOR_2 = 21
PIN_INTERRUPT = 26
PIN_OUTPUT = 16

# Limpieza inicial para evitar conflictos
GPIO.cleanup()  # Fuerza la limpieza de cualquier configuración previa
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIN_OUTPUT, GPIO.OUT)

# Variables globales para PWM
pwm_motor_1 = None
pwm_motor_2 = None

def initialize_pwm():
    """Inicializa los pines PWM con manejo de errores y verificación."""
    global pwm_motor_1, pwm_motor_2

    try:
        # Limpia objetos PWM existentes si es necesario
        if pwm_motor_1 is not None:
            pwm_motor_1.stop()
            pwm_motor_1 = None
        if pwm_motor_2 is not None:
            pwm_motor_2.stop()
            pwm_motor_2 = None

        # Inicializa PWM solo si no están configurados
        pwm_motor_1 = setup_motor(PIN_MOTOR_1)
        pwm_motor_2 = setup_motor(PIN_MOTOR_2)

    except RuntimeError as e:
        print(f"Error al inicializar PWM: {e}")
        GPIO.cleanup()  # Limpieza adicional en caso de error
        raise

def cleanup_pwm():
    """Limpia los recursos PWM y GPIO."""
    global pwm_motor_1, pwm_motor_2
    if pwm_motor_1 is not None:
        pwm_motor_1.stop()
        pwm_motor_1 = None
    if pwm_motor_2 is not None:
        pwm_motor_2.stop()
        pwm_motor_2 = None
    GPIO.cleanup()

# Nueva variable global para almacenar la temperatura personalizada
custom_setpoint = None

def get_setpoint():
    global custom_setpoint
    if custom_setpoint is not None:
        return custom_setpoint  # Usar el valor personalizado si está definido

    current_hour = time.localtime().tm_hour
    if 6 <= current_hour < 20:  # De 6:00 AM a 8:00 PM
        return 12.0  # Temperatura diurna
    else:  # De 8:00 PM a 6:00 AM
        return 24.5  # Temperatura nocturna

def update_custom_setpoint(value):
    global custom_setpoint
    custom_setpoint = value if value is not None else None
    ciclo()  # Re-trigger control cycle with updated setpoint

def solve_temp(setpoint):
   # initialize_pwm()  # Asegura que PWM esté inicializado antes de usarlo
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

def solve_humidity():
    if GPIO.input(PIN_INTERRUPT) == GPIO.HIGH:
        GPIO.output(PIN_OUTPUT, GPIO.HIGH)
        print("Interrupción detectada, PIN 16 en ALTO")
    else:
        GPIO.output(PIN_OUTPUT, GPIO.LOW)

def ciclo():
    """
    Main control cycle for temperature and humidity.
    Dynamically adapts to the current setpoint.
    """
    setpoint = get_setpoint()  # Fetch dynamic or custom setpoint
    control_temperature(setpoint, pid_controller)  # PID temperature control
    solve_temp(setpoint)  # Adjust temperature based on the current setpoint
    solve_humidity()  # Handle humidity control

if __name__ == "__main__":
    try:
        initialize_pwm()  # Inicializa PWM antes de usarlo
        while True:
            ciclo()
            time.sleep(1)  # Evita que el ciclo consuma recursos en exceso
    except KeyboardInterrupt:
        print("Interrupción detectada. Limpiando GPIO...")
