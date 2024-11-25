from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread, Event
from time import sleep
from funciones import update_custom_setpoint, get_setpoint, main
from Temperature import read_temperature

# Configuración del servidor
address = "192.168.1.254"
port = 8080

# Variables globales
current_setpoint = None
setpoint_updated = Event()  # Evento para indicar un cambio en el setpoint


def monitor_setpoint():
    """
    Monitorea los cambios en el setpoint y activa un evento si detecta un cambio.
    """
    global current_setpoint
    while True:
        new_setpoint = get_setpoint()
        if new_setpoint != current_setpoint:
            current_setpoint = new_setpoint
            update_custom_setpoint(current_setpoint)
            print(f"Setpoint actualizado automáticamente: {current_setpoint}°C")
            setpoint_updated.set()  # Marca el evento como activado
        sleep(1)  # Reduce el intervalo para minimizar el delay


def pid_control():
    """
    Control PID en un hilo separado, reinicia automáticamente si cambia el setpoint.
    """
    while True:
        setpoint_updated.wait()  # Espera a que el setpoint cambie
        print("Iniciando/reiniciando control PID...")
        main()  # Ejecuta el control PID con el setpoint actual
        setpoint_updated.clear()  # Resetea el evento hasta el próximo cambio


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
        content_length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            action = data.get("action")
            value = data.get("value")
            response = {}

            if action == "update_setpoint":
                # Actualiza el setpoint manualmente
                global current_setpoint
                current_setpoint = float(value)
                update_custom_setpoint(current_setpoint)
                setpoint_updated.set()  # Marca el evento para reiniciar el control PID
                response["message"] = "Setpoint actualizado e inicio del control PID"

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
        except Exception as e:
            print("Error procesando la solicitud:", e)
            self.send_response(500)
            self.end_headers()


if __name__ == "__main__":
    # Inicia el hilo de monitoreo de setpoint
    Thread(target=monitor_setpoint, daemon=True).start()

    # Inicia el hilo de control PID
    Thread(target=pid_control, daemon=True).start()

    # Inicia el servidor web
    server = HTTPServer((address, port), ControlServer)
    print(f"Servidor corriendo en http://{address}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
        server.server_close()
