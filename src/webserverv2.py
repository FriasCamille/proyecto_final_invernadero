from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from funciones import update_custom_setpoint, get_setpoint, solve_temp
from Temperature import read_temperature

# Configuración del servidor
address = "192.168.1.254"
port = 8080

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
                update_custom_setpoint(float(value))
                response["message"] = "Setpoint actualizado"
            elif action == "get_temperature":
                current_temp = read_temperature()
                response["temperature"] = current_temp
            elif action == "solve_temp":
                setpoint = get_setpoint()
                solve_temp(setpoint)
                response["message"] = "Resolviendo temperatura"

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
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
