from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread
from time import sleep
from funciones import update_custom_setpoint, get_setpoint, main
from Temperature import read_temperature

# Configuración del servidor
address = "192.168.1.254"
port = 8080

# Variable para controlar el hilo del sistema principal
main_thread = None
setpoint_thread = None
current_setpoint = None


def monitor_setpoint():
    """
    Hilo que monitorea y actualiza el setpoint automáticamente.
    Llama a `main` para iniciar el control PID si hay un cambio en el setpoint.
    """
    global current_setpoint, main_thread
    while True:
        new_setpoint = get_setpoint()
        if new_setpoint != current_setpoint:
            current_setpoint = new_setpoint
            update_custom_setpoint(current_setpoint)
            print(f"Setpoint actualizado automáticamente: {current_setpoint}°C")

            # Inicia el sistema PID si no está activo o reinicia con el nuevo setpoint
            if not main_thread or not main_thread.is_alive():
                print("Iniciando el sistema PID con el nuevo setpoint...")
                main_thread = Thread(target=main, daemon=True)
                main_thread.start()
        sleep(1)  # Monitorear cada 5 segundos


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
        global main_thread
        content_length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            action = data.get("action")
            value = data.get("value")
            response = {}

            if action == "update_setpoint":
                # Actualiza el setpoint
                update_custom_setpoint(float(value))
                # Inicia el sistema PID si no está activo
                if not main_thread or not main_thread.is_alive():
                    main_thread = Thread(target=main, daemon=True)
                    main_thread.start()
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
    setpoint_thread = Thread(target=monitor_setpoint, daemon=True)
    setpoint_thread.start()

    # Inicia el servidor web
    server = HTTPServer((address, port), ControlServer)
    print(f"Servidor corriendo en http://{address}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
        server.server_close()
