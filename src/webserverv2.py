from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
from funciones import solve_temp, solve_humidity, get_setpoint, update_custom_setpoint

HOST = "192.168.1.254"
PORT = 8080

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index2.html", "r") as file:
                self.wfile.write(file.read().encode())
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data)
            action = data.get("action")
            value = data.get("value")
            self.handle_action(action, value)
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request")

    def handle_action(self, action, value):
        if action == "default":
            threading.Thread(target=run_default_operation, daemon=True).start()
        elif action == "set_default_temp":
            # Actualizar el setpoint personalizado
            update_custom_setpoint(float(value))
            print(f"Setpoint predeterminado actualizado a {value}°C")
        elif action == "fan":
            # Encendido/apagado del ventilador
            print(f"Ventilador {'encendido' if value else 'apagado'}")
        elif action == "fan_power":
            # Ajustar potencia del ventilador
            print(f"Potencia del ventilador ajustada a {value}%")
        elif action == "light":
            # Encendido/apagado de la luz
            print(f"Luz {'encendida' if value else 'apagada'}")
        elif action == "light_power":
            # Ajustar intensidad de la luz
            print(f"Intensidad de la luz ajustada a {value}%")
        elif action == "pump":
            # Encendido/apagado de la bomba de agua
            print(f"Bomba de agua {'encendida' if value else 'apagada'}")
        else:
            print("Acción no reconocida:", action)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_default_operation():
    """
    Inicia la operación predeterminada en un hilo separado.
    """
    while True:
        setpoint = get_setpoint()
        solve_temp(setpoint)
        solve_humidity()

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), WebServer)
    print(f"Servidor corriendo en http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
