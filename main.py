import requests
import time
from datetime import datetime, timedelta
from barrido import compute_barrido
from grouping import grouping

# Simular la información obtenida de un endpoint
endpoint_url = "https://mabis-backend-ngnfotl6ha-uc.a.run.app/measures/get_measure"

def obtener_datos_del_endpoint():
    try:
        response = requests.get(endpoint_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos: {e}")
        return []

def es_nueva_medicion(time_created, ultimo_tiempo):
    tiempo_medicion = datetime.strptime(time_created, "%Y-%m-%dT%H:%M:%S")
    return tiempo_medicion > ultimo_tiempo

def filtrar_mediciones_recientes(mediciones, ultimo_tiempo):
    mediciones_recientes = [m for m in mediciones if not m.get('measured', False) and es_nueva_medicion(m['time_created'], ultimo_tiempo)]
    return mediciones_recientes

def procesar_datos(nombre, edad, lado):
    compute_barrido(lado.lower())  # Llamar a función de barrido
    na = 16  # Número de áreas en análisis, ajustar según necesario
    M1, f1, rows, cols = grouping(nombre, na, edad, lado.lower())  # Llamar a función de agrupamiento
    print(f"Datos procesados para {nombre}: Matriz={M1}, Frecuencia={f1}, Filas={rows}, Columnas={cols}")

def main():
    ultimo_tiempo = datetime.utcnow() - timedelta(minutes=1)
    ultimo_id = None

    while True:
        mediciones = obtener_datos_del_endpoint()
        mediciones_recientes = filtrar_mediciones_recientes(mediciones, ultimo_tiempo)
        
        for medicion in mediciones_recientes:
            id_actual = medicion.get("id", None)
            if id_actual is None or id_actual == ultimo_id:
                continue
            
            nombre = f"{medicion.get('name', '')} {medicion.get('last_name', '')}"
            lado = medicion.get("side", "")
            diagnostico = medicion.get("diagnostico", "")
            edad = "Desconocida"  # Si no se proporciona, reemplazar con datos por defecto
            time_created = medicion['time_created']
            
            procesar_datos(nombre, edad, lado)
            print(f"Nuevo registro: {nombre}, {edad}, {lado}, {diagnostico}, Creado: {time_created}")
            
            ultimo_tiempo = datetime.strptime(time_created, "%Y-%m-%dT%H:%M:%S")
            ultimo_id = id_actual
        
        time.sleep(1)

if __name__ == "__main__":
    main()
