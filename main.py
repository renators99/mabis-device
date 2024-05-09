import requests
import time
from datetime import datetime, timedelta
from grouping import grouping
from barrido import compute_barrido

# Simular la información obtenida de un endpoint
endpoint_url = "https://mabis-frontend-ngnfotl6ha-ue.a.run.app/measures/get_measure"  # Cambia esta URL por tu endpoint real

# Obtener datos desde el endpoint
def obtener_datos_del_endpoint():
    try:
        response = requests.get(endpoint_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos: {e}")
        return []

# Procesar los datos de la medición
def procesar_datos(nombre, edad, lado):
    compute_barrido(lado)
    na = 16  # Cambiar este valor si es necesario
    M1, f1, rows, cols = grouping(nombre, na, edad, lado)
    print(f"Datos procesados para {nombre}: {M1}, {f1}, {rows}, {cols}")

# Verificar si una medición es nueva (en el último minuto)
def es_nueva_medicion(time_created):
    ahora = datetime.utcnow()
    tiempo_medicion = datetime.strptime(time_created, "%Y-%m-%dT%H:%M:%S")
    return ahora - tiempo_medicion < timedelta(minutes=1)

# Filtrar mediciones recientes no medidas
def filtrar_mediciones_recientes(mediciones):
    mediciones_recientes = [m for m in mediciones if not m['measured'] and es_nueva_medicion(m['time_created'])]
    return mediciones_recientes

# Bucle principal para obtener y procesar mediciones recientes
def main():
    while True:
        mediciones = obtener_datos_del_endpoint()
        mediciones_recientes = filtrar_mediciones_recientes(mediciones)
        
        for medicion in mediciones_recientes:
            nombre = f"{medicion.get('name', '')} {medicion.get('last_name', '')}"
            lado = medicion.get("side", "")
            diagnostico = medicion.get("diagnostico", "")
            edad = "Desconocida"  # Si no se proporciona, reemplazar con datos por defecto
            
            procesar_datos(nombre, edad, lado)
        
        # Esperar 1 segundo antes de la siguiente solicitud
        time.sleep(1)

if __name__ == "__main__":
    main()