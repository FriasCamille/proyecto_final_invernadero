import smbus2
import struct
import threading
import time
from Temperature import read_temperature  

SLAVE_ADDR = 0x0A  
i2c = smbus2.SMBus(1)


Kp = 3.0  
Ki = 2.5  
Kd = 1.5  


integral = 0
previous_error = 0


def pid_control(setpoint, actual_value, dt=1.0):
    global integral, previous_error
    error = setpoint - actual_value
    integral += error * dt
    derivative = (error - previous_error) / dt
    output = Kp * error + Ki * integral + Kd * derivative
    previous_error = error


    output = max(0, min(100, output))  
    output = round(output)  
    return output


def writePower(pwr):
    try:
        data = struct.pack('<f', pwr)  
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
        i2c.i2c_rdwr(msg)  
    except Exception as e:
        print(f"Error en la escritura I2C: {e}")


def control_thread():
    setpoint = float(input("Introduce la temperatura deseada (°C): "))
    print("Iniciando control PID con sensores DS18B20...")
    while True:
        try:
            actual_temp = read_temperature()  
            if actual_temp is None:
                print("No se obtuvo una lectura válida. Intentando de nuevo...")
                time.sleep(1)
                continue

            adjusted_power = pid_control(setpoint, actual_temp)  
            writePower(adjusted_power)  


            print(f"Setpoint: {setpoint}°C | Actual: {actual_temp:.2f}°C | Potencia: {adjusted_power}%")
            time.sleep(1)  
        except Exception as e:
            print(f"Error en el control PID: {e}")
            time.sleep(1)  


thread = threading.Thread(target=control_thread)
thread.start()
