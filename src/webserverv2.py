from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread, Lock
from motorPWM import setup_motor, set_motor_power, toggle_fan, cleanup

# Configuración del servidor
address = "192.168.1.254"
port = 8080

# Configuración de GPIO para los ventiladores
GPIO_PIN_FAN1 = 20
GPIO_PIN_FAN2 = 21
fan_pwm1 = None
fan_pwm2 = None

# Inicialización de los ventiladores
def initialize_fans():
    """
    Inicializa los ventiladores.
    """
    global fan_pwm1, fan_pwm2
    fan_pwm1 = setup_motor(GPIO_PIN_FAN1)
    fan_pwm2 = setup_motor(GPIO_PIN_FAN2)


def control_fan(fan, power=None, state=None):
    """
    Controla el estado o la potencia del ventilador.
    """
    if state is not None:
        toggle_fan(fan, state)
    if power is not None:
        if fan == "fan1":
            set_motor_power(fan_pwm1, power, "fan1")
        elif fan == "fan2":
            set_motor_power(fan_pwm2, power, "fan2")


class ControlServer(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            action = data.get("action")
            fan = data.get("fan")  # "fan1" o "fan2"
            power = data.get("power")
            state = data.get("state")  # True para encender, False para apagar
            response = {}

            if action == "toggle_fan":
                control_fan(fan, state=state)
                response["message"] = f"{fan} {'encendido' if state else 'apagado'}"
            elif action == "set_power":
                control_fan(fan, power=power)
                response["message"] = f"Potencia del {fan} ajustada a {power}%"

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
