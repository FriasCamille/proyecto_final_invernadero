from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from threading import Thread
from time import sleep
from funciones import (
    encender_motor,
    apagar_motor,
    encender_ambos_motores,
    apagar_ambos_motores,
    ajustar_potencia_motor,
    ajustar_potencia_ambos_motores,
    pwm_motor_1,
    pwm_motor_2,
    get_setpoint,
    update_custom_setpoint,
    main
)
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
        sleep(5)  # Monitorear cada 5 segundos


class ControlServer(BaseHTTPRequestHandler):
    def _serve_ui_file(self):
        """
        Sirve el archivo HTML para la interfaz de usuario.
        """
        try:
            with open("index.html", "r") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(content, "utf-8"))
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Archivo HTML no encontrado")

    def do_GET(self):
        """
        Maneja solicitudes GET para servir la interfaz o datos específicos.
        """
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
        """
        Maneja solicitudes POST para controlar motores y actualizar configuraciones.
        """
        global main_thread
        content_length = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            action = data.get("action")
            value = data.get("value")
            response = {}

            if action == "motor_1_on":
                encender_motor(pwm_motor_1)
                response["message"] = "Motor 1 encendido"
            elif action == "motor_1_off":
                apagar_motor(pwm_motor_1)
                response["message"] = "Motor 1 apagado"
            elif action == "motor_2_on":
                encender_motor(pwm_motor_2)
                response["message"] = "Motor 2 encendido"
            elif action == "motor_2_off":
                apagar_motor(pwm_motor_2)
                response["message"] = "Motor 2 apagado"
            elif action == "motors_on":
                encender_ambos_motores()
                response["message"] = "Ambos motores encendidos"
            elif action == "motors_off":
                apagar_ambos_motores()
                response["message"] = "Ambos motores apagados"
            elif action == "set_motor_1_power":
                ajustar_potencia_motor(pwm_motor_1, float(value))
                response["message"] = f"Potencia del Motor 1 ajustada a {value}%"
            elif action == "set_motor_2_power":
                ajustar_potencia_motor(pwm_motor_2, float(value))
                response["message"] = f"Potencia del Motor 2 ajustada a {value}%"
            elif action == "set_both_power":
                ajustar_potencia_ambos_motores(float(value))
                response["message"] = f"Potencia de ambos motores ajustada a {value}%"
            elif action == "update_setpoint":
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
