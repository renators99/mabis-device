import numpy as np
import pandas as pd
import os
from datetime import datetime
from math import pi

def grouping(nombre, apellido, lado, fecha, na):
    # Convertir a mayúsculas y preparar los nombres de las carpetas
    nombre_upper = nombre.upper()
    apellido_upper = apellido.upper()
    lado_upper = lado.upper()
    
    # Formatear la fecha a YYYYMMDD y convertir a mayúsculas
    fecha_fmt = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d").upper()
    
    # Carpeta madre: NOMBRE_APELLIDO_FECHA en mayúsculas
    base_dir = f"{nombre_upper}_{apellido_upper}_{fecha_fmt}"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Subcarpeta para el lado específico: NOMBRE_APELLIDO_LADO en mayúsculas
    side_dir = f"{nombre_upper}_{apellido_upper}_{lado_upper}"
    full_dir = os.path.join(base_dir, side_dir)
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)

    M1 = []  # Lista para almacenar las señales agrupadas
    pos = 'A' if lado.lower() == 'izquierda' else 'B' if lado.lower() == 'derecha' else 'X'
    L = 'IZQ' if lado.lower() == 'izquierda' else 'DER' if lado.lower() == 'derecha' else 'INDEF'

    for i in range(1, na + 1):
        for j in range(1, na + 1):
            # Leer los archivos CSV de resultados
            name_file = os.path.join('datos', f'resultsSOLT{pos}_p{i}_{j}.csv')
            v = pd.read_csv(name_file, header=0)
            vm = v.iloc[:, 0].values  # magnitudes
            vp = v.iloc[:, 1].values  # fases
            f = v.iloc[:, 2].values  # frecuencias
            Sp = 10 ** (vm / 20) * np.exp(1j * vp * pi / 180)  # Conversión de magnitud y fase a números complejos

            for m in range(len(Sp)):
                if Sp[m].imag >= 0:
                    M1.append(f"{Sp[m].real:.6f}+{Sp[m].imag:.6f}j")
                else:
                    M1.append(f"{Sp[m].real:.6f}{Sp[m].imag:.6f}j")

    # Organizar los datos en una matriz y un DataFrame
    M1 = np.array(M1).reshape(na * na, len(vm)).T
    M1 = pd.DataFrame(data=M1)
    f1 = pd.DataFrame(data=f).to_numpy() * 10**6
    rows, cols = np.shape(M1)

    # Guardar los resultados en la carpeta del lado correspondiente
    output_file = os.path.join(full_dir, f'resultsSOLT{L}.csv')
    M1.to_csv(output_file, index=False, header=False)

    M1 = M1.to_numpy().astype(complex)
    return M1, f1, rows, cols

