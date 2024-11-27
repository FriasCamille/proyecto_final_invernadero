import smbus2
import struct
import time
from Temperature import read_temperature  

SLAVE_ADDR = 0x0A  
i2c = smbus2.SMBus(1)

class PIDController:
    def __init__(self, kp=3.0, ki=2.5, kd=1.5):
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd
        self.integral = 0
        self.previous_error = 0
        self.last_time = time.time()

    def calculate(self, setpoint, actual_value):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        error = setpoint - actual_value
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt if dt > 0 else 0

        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.previous_error = error

        output = max(0, min(100, output))  
        return round(output)

def write_power(pwr):
    try:
        data = struct.pack('<f', pwr)  
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
        i2c.i2c_rdwr(msg)  
    except Exception as e:
        print(f"Error en la escritura I2C: {e}")

def control_temperature(setpoint, pid_controller):
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
