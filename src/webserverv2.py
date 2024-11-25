from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread, Event
from time import sleep
from motorPWM import setup_motor, set_motor_power, cleanup
from funciones import update_custom_setpoint, get_setpoint, main
from Temperature import read_temperature

# Configuración del servidor
address = "192.168.1.254"
port = 8080

# Variables globales
current_setpoint = None
setpoint_updated = Event()  # Evento para indicar un cambio en el setpoint
fan_thread = None
fan_pwm = setup_motor(20)  # Configura el motor en el pin 20

# Hilo para el control de ventiladores
def control_fan(power, action):
    """
    Controla el estado de los ventiladores.
    """
    if action == "on":
        set_motor_power(fan_pwm, power)
        print(f"Ventilador encendido con potencia: {power}%")
    elif action == "off":
        set_motor_power(fan_pwm, 0)
        print("Ventilador apagado")


class ControlServer(BaseHTTPRequestHandler):
    def _serve_ui_file(self):
        with open("control_interface.html", "r") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))

    def do_GET(self):
        if self.path == "/":
            self._serve_ui_file()
        elif self.path == "/temperature":
            # Devuelve la temperatura actual en JSON
            current_temp = read_temperature()
            response = {"temperature": current_temp}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
        else:
            self.send_error(404)

    def do_POST(self):
        global fan_thread
        content_length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            action = data.get("action")
            value = data.get("value")
            power = int(data.get("power", 0))  # Potencia por defecto 0
            response = {}

            if action == "update_setpoint":
                # Actualiza el setpoint manualmente
                global current_setpoint
                current_setpoint = float(value)
                update_custom_setpoint(current_setpoint)
                setpoint_updated.set()  # Marca el evento para reiniciar el control PID
                response["message"] = "Setpoint actualizado e inicio del control PID"

            elif action == "control_fan":
                if value == "on":
                    Thread(target=control_fan, args=(power, "on"), daemon=True).start()
                    response["message"] = f"Ventilador encendido con potencia: {power}%"
                elif value == "off":
                    Thread(target=control_fan, args=(0, "off"), daemon=True).start()
                    response["message"] = "Ventilador apagado"

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
        except Exception as e:
            print("Error procesando la solicitud: {}".format(e))
            self.send_response(500)
            self.end_headers()


if __name__ == "__main__":
    # Inicia el servidor web
    server = HTTPServer((address, port), ControlServer)
    print("Servidor corriendo en http://{}:{}".format(address, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
        cleanup()
