from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from funciones import control_irrigacion, set_temperatura, control_ventilador

HOST = "192.168.1.254"
PORT = 8080

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "r") as file:
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
        if action == "irrigation":
            control_irrigacion(value)
        elif action == "set_temp":
            set_temperatura(value)
        elif action == "fan":
            control_ventilador(value)
        else:
            print("Acci  n no reconocida:", action)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), WebServer)
    print(f"Servidor corriendo en http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt: