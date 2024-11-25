import smbus2
import struct
import time
from Temperature import read_temperature  

SLAVE_ADDR = 0x0A  
i2c = smbus2.SMBus(1)

class PIDController:
    def __init__(self, kp=3.0, ki=2.5, kd=1.5):
        """
        Inicializa el controlador PID con los valores por defecto proporcionados.
        
        :param kp: Coeficiente proporcional (default=3.0).
        :param ki: Coeficiente integral (default=2.5).
        :param kd: Coeficiente derivativo (default=1.5).
        """
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd
        self.integral = 0
        self.previous_error = 0

    def calculate(self, setpoint, actual_value, dt=1.0):
        """
        Calcula la salida del PID en función del setpoint y la temperatura actual.

        :param setpoint: Temperatura deseada.
        :param actual_value: Temperatura actual.
        :param dt: Intervalo de tiempo desde la última medición (default=1.0).
        :return: Salida limitada entre 0% y 100%.
        """
        error = setpoint - actual_value
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.previous_error = error

        # Limitar salida entre 0% y 100%
        output = max(0, min(100, output))  
        return round(output)

def write_power(pwr):
    """
    Escribe el nivel de potencia en el dispositivo a través de I2C.

    :param pwr: Nivel de potencia a enviar (0-100).
    """
    try:
        data = struct.pack('<f', pwr)  
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
        i2c.i2c_rdwr(msg)  
    except Exception as e:
        print(f"Error en la escritura I2C: {e}")

def control_temperature(setpoint):
    """
    Realiza el control PID para mantener la temperatura deseada.

    :param setpoint: Temperatura deseada.
    """
    pid_controller = PIDController()  # Usa las constantes predeterminadas
    try:
        actual_temp = read_temperature()
        if actual_temp is None:
            print("No se obtuvo una lectura válida. Intentando de nuevo...")
            return None

        adjusted_power = pid_controller.calculate(setpoint, actual_temp)
        write_power(adjusted_power)

        print(f"Setpoint: {setpoint}°C | Actual: {actual_temp:.2f}°C | Potencia: {adjusted_power}%")
        return adjusted_power
    except Exception as e:
        print(f"Error en el control PID: {e}")
        return None

