import time
import requests
import subprocess
from tkinter import *
from datetime import datetime, timedelta
from barrido import compute_barrido
from grouping import grouping

# Variable global para almacenar el id del último registro medido
last_measured_id = None

def fetch_data():
    """Función para obtener datos del endpoint y procesar solo el último registro si es reciente y no ha sido medido antes."""
    global last_measured_id
    url = "https://mabis-backend-ngnfotl6ha-uc.a.run.app/measures/get_measure"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para respuestas no exitosas
        data = response.json()
        if data:  # Verifica que la lista no esté vacía
            last_record = data[-1]  # Obtiene el último registro
            # Imprime los detalles del último registro
            print("Último registro obtenido:", last_record)
            # Comprueba si el último registro es reciente y no ha sido medido antes
            if last_record['id'] != last_measured_id and is_recent(last_record.get("time_created")):
                last_measured_id = last_record['id']  # Actualiza el id del último registro medido
                extraer(last_record)
            else:
                print("El último registro no es lo suficientemente reciente o ya ha sido medido.")
    except requests.RequestException as e:
        print(f"Error al obtener datos: {e}")
    finally:
        # Programar la próxima ejecución de esta misma función después de 5000 milisegundos (5 segundos)
        raiz.after(5000, fetch_data)

def is_recent(time_str):
    """Verifica si la fecha y hora proporcionadas están dentro de los últimos dos minutos."""
    record_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    now = datetime.now()
    two_minutes_ago = now - timedelta(minutes=2)
    return record_time >= two_minutes_ago

def extraer(data):
    """Función para extraer y procesar los datos obtenidos."""
    if data:
        nombre = data.get('name', '').upper()
        apellido = data.get('last_name', '').upper()
        lado = data.get("side", "").upper()
        fecha = data.get("time_created", datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
        na = 8  # Asume que `na` es un valor fijo o puedes ajustarlo según la data
        compute_barrido(lado)
        M1, f1, rows, cols = grouping(nombre, apellido, lado, fecha, na)
        print("Procesamiento completado para:", f"{nombre} {apellido}")
    else:
        print("No se recibieron datos para procesar.")

def open_vna_program():
    """Función para abrir el programa VNA."""
    try:
        subprocess.Popen(["C:\\VNA\\S2VNA\\S2VNA.exe"])  # Asegúrate de poner la ruta correcta al ejecutable del VNA
    except Exception as e:
        print(f"Error al abrir el programa VNA: {e}")

raiz = Tk()
raiz.title("MABIS")
raiz.config(bg="skyblue")

miframe = Frame(raiz, bg="white", width=650, height=350)
miframe.pack()
miframe.config(bd=20)
miframe.config(relief="groove")
miframe.config(cursor="hand2")

milabel = Label(miframe, text="Proyecto 'MABIS'", fg="black", bg="white", font=("Open Sans", 18))
milabel.place(x=200, y=0)

# Iniciar peticiones automáticas y abrir programa VNA al iniciar la GUI
open_vna_program()
time.sleep(5)  # Espera 5 segundos antes de comenzar a buscar datos
fetch_data()

raiz.mainloop()

