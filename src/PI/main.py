from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import signal
import sys
import threading
import time
from datetime import datetime, timedelta
from control import motor_derecho, motor_izquierdo, ambos_motore, bomba, potencia_foco, set_PID, temperatura, cleanup, predeterminado, set_value
import matplotlib.pyplot as plt

HOST = "0.0.0.0"
PORT = 8080

# Variable global para almacenar la temperatura
current_temperature = {"average": None}

# Función para actualizar la temperatura periódicamente en un hilo
def update_temperature():
    """
    Hilo en segundo plano que actualiza la temperatura cada 5 segundos.
    """
    global current_temperature
    while True:
        try:
            temp = temperatura()  # Llama a la función para leer la temperatura
            if temp is not None:
                current_temperature["average"] = temp
                print(f"[Hilo Temperatura] Temperatura actualizada: {temp:.2f}°C")
            else:
                current_temperature["average"] = None
                print("[Hilo Temperatura] No se pudo obtener una temperatura válida.")
        except Exception as e:
            print(f"[Hilo Temperatura] Error actualizando la temperatura: {e}")
            current_temperature["average"] = None  # Manejo explícito de errores
        time.sleep(5)  # Espera 5 segundos antes de la siguiente lectura

def log_action(action, message):
    """
    Función para registrar las acciones en una bitácora.
    """
    with open('bitacora_acciones.txt', 'a') as log_file:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - Acción: {action} - {message}\n")

def read_log_file(file_path, time_limit):
    """
    Lee un archivo de bitácora y devuelve los registros dentro del límite de tiempo especificado.
    """
    data = {"timestamps": [], "values": []}
    time_limit = datetime.now() - timedelta(minutes=time_limit)
    with open(file_path, 'r') as log_file:
        for line in log_file:
            timestamp_str, value = line.split(" - ")[0], line.split(" - ")[-1]
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            if timestamp >= time_limit:
                data["timestamps"].append(timestamp_str)
                data["values"].append(value.strip())
    return data

def generate_temperature_chart():
    """
    Genera una gráfica de temperatura de los últimos 5 minutos y la guarda como imagen.
    """
    data = read_log_file('BitacoraTemp.txt', 5)
    timestamps = data["timestamps"]
    temperatures = [float(value.split(": ")[1].replace("°C", "")) for value in data["values"]]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, temperatures, marker='o')
    plt.title('Temperatura de los últimos 5 minutos')
    plt.xlabel('Tiempo')
    plt.ylabel('Temperatura (°C)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('temperature_chart.png')
    plt.close()

def generate_action_chart():
    """
    Genera una gráfica de acciones de los últimos 5 minutos y la guarda como imagen.
    """
    data = read_log_file('bitacora_acciones.txt', 5)
    timestamps = data["timestamps"]
    actions = data["values"]

    plt.figure(figsize=(10, 5))
    plt.bar(timestamps, range(len(actions)), tick_label=actions)
    plt.title('Acciones de los últimos 5 minutos')
    plt.xlabel('Tiempo')
    plt.ylabel('Acciones')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('action_chart.png')
    plt.close()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("interface.html", "r") as file:
                self.wfile.write(file.read().encode("utf-8"))
        elif self.path == "/temperature-chart":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open("temperature_chart.png", "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/action-chart":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open("action_chart.png", "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/temperature-data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = read_log_file('BitacoraTemp.txt', 5)
            temperatures = [float(value.split(": ")[1].replace("°C", "")) for value in data["values"]]
            response_data = {"timestamps": data["timestamps"], "temperatures": temperatures}
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        elif self.path == "/action-data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            data = read_log_file('bitacora_acciones.txt', 5)
            actions = [value for value in data["values"]]
            response_data = {"timestamps": data["timestamps"], "actions": actions}
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            self.send_error(404, "Archivo no encontrado.")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode("utf-8"))
            action = data.get("action")
            value = data.get("value")

            response_data = {"status": "success"}
            
            # Manejo de acciones
            if action == "motor_derecho":
                motor_derecho(value)
                message = f"Motor derecho ajustado al {value}%"
                response_data["message"] = message
            elif action == "motor_izquierdo":
                motor_izquierdo(value)
                message = f"Motor izquierdo ajustado al {value}%"
                response_data["message"] = message
            elif action == "ambos_motores":
                ambos_motore(value)
                message = f"Ambos motores ajustados al {value}%"
                response_data["message"] = message
            elif action == "bomba":
                bomba(value)
                message = "Bomba encendida" if value == 1 else "Bomba apagada"
                response_data["message"] = message
            elif action == "foco":
                potencia_foco(value)
                message = f"Foco ajustado al {value}% de potencia"
                response_data["message"] = message
            elif action == "set_pid":
                set_PID(value)
                message = f"PID ajustado a {value}°C"
                response_data["message"] = message
            elif action == "temperatura":
                # Devuelve la temperatura almacenada en la variable global
                temp = current_temperature["average"]
                message = f"Temperatura promedio: {temp:.2f}°C" if temp is not None else "Temperatura no disponible"
                response_data["message"] = message
            
            # Nuevas funcionalidades
            elif action == "predeterminado":
                predeterminado()
                message = "Modo predeterminado activado"
                response_data["message"] = message
            elif action == "set_value":
                temp = value
                set_value(temp)
                message = f"Setpoint configurado a {temp}°C"
                response_data["message"] = message
            
            else:
                raise ValueError("Acción no reconocida")

            # Registrar la acción en la bitácora
            log_action(action, message)

            # Respuesta HTTP exitosa
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        except Exception as e:
            # Respuesta en caso de error
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

def cleanup_and_exit(server):
    """
    Función para cerrar el servidor y liberar recursos de forma segura.
    """
    print("\nCerrando servidor y limpiando recursos...")
    try:
        cleanup()  # Limpia los pines GPIO en el archivo control.py
    except Exception as e:
        print(f"Error durante la limpieza: {e}")
    finally:
        server.server_close()  # Cierra el servidor HTTP
        print("Servidor detenido y recursos limpiados. ¡Adiós!")
        sys.exit(0)

def signal_handler(sig, frame):
    """
    Captura señales como CTRL+C y llama a la limpieza segura.
    """
    cleanup_and_exit(httpd)

if __name__ == "__main__":
    # Inicia el hilo para actualizar la temperatura
    temperature_thread = threading.Thread(target=update_temperature, daemon=True)
    temperature_thread.start()

    # Captura la señal SIGINT (CTRL+C) para limpiar y salir de forma segura
    signal.signal(signal.SIGINT, signal_handler)

    # Inicia el servidor HTTP
    httpd = HTTPServer((HOST, PORT), RequestHandler)
    print(f"Servidor iniciado en http://{HOST}:{PORT}")

    # Genera las gráficas cada minuto
    def generate_charts_periodically():
        while True:
            generate_temperature_chart()
            generate_action_chart()
            time.sleep(60)

    chart_thread = threading.Thread(target=generate_charts_periodically, daemon=True)
    chart_thread.start()

    try:
        # Mantiene el servidor corriendo
        httpd.serve_forever()
    except KeyboardInterrupt:
        cleanup_and_exit(httpd)
    except Exception as e:
        print(f"Error inesperado: {e}")
        cleanup_and_exit(httpd)
