from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from funciones import update_custom_setpoint, solve_temp, solve_humidity, get_setpoint

# Configuración del servidor
address = "192.168.1.254"
port = 8080

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
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            action = data.get("action")
            value = data.get("value")

            if action == "update_setpoint":
                update_custom_setpoint(float(value))
            elif action == "solve_temp":
                solve_temp(get_setpoint())  # Asume que `get_setpoint` está importado
            elif action == "solve_humidity":
                solve_humidity()
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            print("Error procesando la solicitud:", e)
            self.send_response(500)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer((address, port), ControlServer)
    print(f"Servidor corriendo en http://{address}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
        server.server_close()
