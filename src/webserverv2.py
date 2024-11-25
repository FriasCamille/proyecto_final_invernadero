from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread, Lock
from motorPWM import setup_motor, set_motor_power, cleanup
from Temperature import read_temperature

# Configuración del servidor
address = "192.168.1.254"
port = 8080

# Configuración de GPIO para el ventilador
GPIO_PIN_FAN = 20
fan_pwm = None  # PWM del ventilador
fan_lock = Lock()  # Evita configuraciones concurrentes


def initialize_fan():
    """
    Inicializa el PWM para el ventilador.
    """
    global fan_pwm
    try:
        cleanup()  # Limpia configuraciones previas
        fan_pwm = setup_motor(GPIO_PIN_FAN)
    except RuntimeError as e:
        print("Error inicializando ventilador:", e)


def control_fan(power, action):
    """
    Controla el estado de los ventiladores.
    """
    global fan_pwm
    with fan_lock:  # Asegura que solo un hilo configure el ventilador a la vez
        if action == "on":
            if 0 <= power <= 100:
                set_motor_power(fan_pwm, power)
                print(f"Ventilador encendido con potencia: {power}%")
            else:
                print("Error: Potencia fuera de rango (0-100)")
        elif action == "off":
            set_motor_power(fan_pwm, 0)
            print("Ventilador apagado")


class ControlServer(BaseHTTPRequestHandler):
    def _serve_ui_file(self):
        with open("indexv2.html", "r") as f:
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
        content_length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            action = data.get("action")
            value = data.get("value")
            power = int(data.get("power", 0))  # Potencia por defecto 0
            response = {}

            if action == "control_fan":
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
    initialize_fan()  # Inicializa el ventilador

    # Inicia el servidor web
    server = HTTPServer((address, port), ControlServer)
    print("Servidor corriendo en http://{}:{}".format(address, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
        cleanup()
