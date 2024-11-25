from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread, Lock
from motorPWM import setup_motor, set_motor_power, cleanup

# Configuración del servidor
address = "192.168.1.254"
port = 8080

# Pines GPIO para los ventiladores
GPIO_PIN_FAN1 = 20
GPIO_PIN_FAN2 = 21
fan_pwm1 = None
fan_pwm2 = None
fan_states = {"fan1": False, "fan2": False}  # Estados de los ventiladores
fan_lock = Lock()  # Evita configuraciones concurrentes


def initialize_fans():
    """
    Inicializa los ventiladores.
    """
    global fan_pwm1, fan_pwm2
    try:
        cleanup()  # Limpia configuraciones previas
        fan_pwm1 = setup_motor(GPIO_PIN_FAN1)
        fan_pwm2 = setup_motor(GPIO_PIN_FAN2)
    except RuntimeError as e:
        print("Error inicializando ventiladores:", e)


def control_fan(fan, power=None, action=None):
    """
    Controla el estado o la potencia del ventilador.

    Args:
        fan: "fan1" o "fan2".
        power: Potencia deseada (0-100).
        action: "on" o "off".
    """
    global fan_states
    with fan_lock:
        if action == "on":
            fan_states[fan] = True
            print(f"{fan} encendido")
        elif action == "off":
            fan_states[fan] = False
            print(f"{fan} apagado")
            if fan == "fan1":
                set_motor_power(fan_pwm1, 0, "fan1")
            elif fan == "fan2":
                set_motor_power(fan_pwm2, 0, "fan2")

        if power is not None:
            if fan_states[fan]:  # Solo ajusta potencia si el ventilador está encendido
                if fan == "fan1":
                    set_motor_power(fan_pwm1, power, "fan1")
                elif fan == "fan2":
                    set_motor_power(fan_pwm2, power, "fan2")
                print(f"Potencia de {fan} ajustada a {power}%")
            else:
                print(f"No se puede ajustar la potencia de {fan} porque está apagado.")


class ControlServer(BaseHTTPRequestHandler):
    def _serve_ui_file(self):
        """
        Sirve el archivo HTML al cliente.
        """
        try:
            with open("indexv2.html", "r") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(content, "utf-8"))
        except FileNotFoundError:
            self.send_error(404, "Archivo HTML no encontrado")

    def do_GET(self):
        """
        Maneja solicitudes GET para servir el archivo HTML o datos.
        """
        if self.path == "/":
            self._serve_ui_file()
        elif self.path == "/status":
            # Devuelve el estado de los ventiladores
            response = {
                "fan1": {"state": fan_states["fan1"]},
                "fan2": {"state": fan_states["fan2"]}
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
        else:
            self.send_error(404)

    def do_POST(self):
        """
        Maneja solicitudes POST para controlar los ventiladores.
        """
        content_length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            action = data.get("action")  # "on" o "off"
            fan = data.get("fan")  # "fan1" o "fan2"
            power = data.get("power")  # Potencia
            response = {}

            if action in ["on", "off"]:
                control_fan(fan, action=action)
                response["message"] = f"{fan} {'encendido' if action == 'on' else 'apagado'}"
            elif action == "set_power":
                control_fan(fan, power=int(power))
                response["message"] = f"Potencia de {fan} ajustada a {power}%"

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
        except Exception as e:
            print("Error procesando la solicitud:", e)
            self.send_response(500)
            self.end_headers()


if __name__ == "__main__":
    initialize_fans()  # Inicializa los ventiladores
    server = HTTPServer((address, port), ControlServer)
    print(f"Servidor corriendo en http://{address}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
        cleanup()
