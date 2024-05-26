import requests
from tkinter import *
from datetime import datetime, timezone, timedelta
import threading
import time
from grouping import grouping
from barrido import compute_barrido

# Variables para almacenar los datos del último paciente
ultimo_paciente = {}

# Función para obtener datos del endpoint
def obtener_datos_del_endpoint():
    while True:
        endpoint_url = "https://mabis-backend-ngnfotl6ha-uc.a.run.app/measures/get_measure"
        print("Realizando una solicitud al endpoint...")
        try:
            response = requests.get(endpoint_url)
            response.raise_for_status()  # Lanzará una excepción si la respuesta no es satisfactoria
            mediciones = response.json()
            procesar_mediciones(mediciones)
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos: {e}")
        time.sleep(10)  # Espera 10 segundos antes de hacer otra solicitud

# Función para procesar las mediciones y actualizar la interfaz
def procesar_mediciones(mediciones):
    global ultimo_paciente
    for medicion in mediciones:
        if es_medicion_reciente(medicion['time_created']):
            ultimo_paciente = medicion
            actualizar_interfaz()
            break

# Función para verificar si una medición es reciente
def es_medicion_reciente(time_created):
    tiempo_limite = datetime.now(timezone.utc) - timedelta(minutes=2)
    tiempo_medicion = datetime.strptime(time_created, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    return tiempo_medicion > tiempo_limite

# Función para actualizar la interfaz con los datos del paciente
def actualizar_interfaz():
    if ultimo_paciente:
        nombre = f"{ultimo_paciente.get('name', '')} {ultimo_paciente.get('last_name', '')}".strip()
        lado = ultimo_paciente.get('side', 'Desconocida').capitalize()
        edad = str(ultimo_paciente.get('age', ''))
        nombre_label_valor.config(text=nombre)
        lado_label_valor.config(text=lado)

def iniciar_analisis():
    if ultimo_paciente:
        nombre = f"{ultimo_paciente.get('name', '')} {ultimo_paciente.get('last_name', '')}".strip()
        lado = ultimo_paciente.get('side', 'Desconocida').capitalize()
        compute_barrido(lado)
        na = 16
        M1, f1, rows, cols = grouping(nombre, na, lado)
        print(f"Datos procesados para {nombre}: Matriz M1 de tamaño {rows}x{cols}, Frecuencias: {f1.shape}")

# Configuración de la interfaz gráfica
raiz = Tk()
raiz.title("MABIS")
raiz.iconbitmap("img/cancer.ico")

miframe = Frame(raiz, width=650, height=350)
miframe.pack()
miframe.config(bd=20, relief="groove", cursor="hand2")

milabel = Label(miframe, text="Proyecto 'MABIS'", fg="red", font=("Comic Sans MS", 18))
milabel.place(x=200, y=0)

imagen = PhotoImage(file="img/cancr1.png")
Label(miframe, image=imagen).place(x=90, y=0)

milabel = Label(miframe, text="Barrido", fg="red", font=("Comic Sans MS", 14))
milabel.place(x=250, y=60)

nombre_label = Label(miframe, text="Nombre y Apellidos: ")
nombre_label.place(x=10, y=100)
nombre_label_valor = Label(miframe, text="")
nombre_label_valor.place(x=190, y=100)

lado_label = Label(miframe, text="Lado: ")
lado_label.place(x=10, y=130)
lado_label_valor = Label(miframe, text="")
lado_label_valor.place(x=190, y=130)

botonStart = Button(miframe, text="Empezar", command=iniciar_analisis)
botonStart.place(x=200, y=240)

# Inicia el hilo para consultar el endpoint continuamente
thread = threading.Thread(target=obtener_datos_del_endpoint)
thread.daemon = True  # Esto asegura que el hilo se cerrará cuando se cierre la aplicación
thread.start()

raiz.mainloop()

