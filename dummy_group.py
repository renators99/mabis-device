import numpy as np
import pandas as pd
from math import pi

def grouping(n1, na, edad, lado):
    """
    Agrupa datos de mediciones de archivos CSV, calcula la representación en números complejos
    y guarda los resultados en otro archivo CSV.

    Args:
    n1 (str): Prefijo para el nombre del archivo de salida.
    na (int): Número de antenas o rangos en cada lado.
    edad (str): Edad o identificador adicional para el archivo.
    lado (str): 'izquierda' o 'derecha' indicando el lado de las mediciones.

    Returns:
    tuple: Contiene la matriz de señales agrupadas como números complejos, frecuencias,
           número de filas y número de columnas de la matriz.
    """
    M1 = []  # columnas (señales con tumor) agrupadas
    Pos = 'A' if lado == 'izquierda' else 'B'
    L = 'Izq' if lado == 'izquierda' else 'Der'

    for i in range(1, na + 1):
        for j in range(1, na + 1):
            name_file = f'datos/resultsSOLT{Pos}_p{i}_{j}.csv'  # Definiendo archivo de lectura
            try:
                v = pd.read_csv(name_file, header=0)  # Leyendo csv del archivo
                vm = v.iloc[:, 0].values  # magnitud
                vp = v.iloc[:, 1].values  # fase
                f = v.iloc[:, 2].values  # frecuencia
                Sp = 10 ** (vm / 20) * np.exp(1j * vp * pi / 180)  # Conversión de fase a número complejo

                # Agrupando señales y convirtiendo a str
                M1.extend([f'{sp.real}+{sp.imag}j' if sp.imag >= 0 else f'{sp.real}{sp.imag}j' for sp in Sp])
            except FileNotFoundError:
                print(f"No se encontró el archivo {name_file}")

    M1 = np.array(M1).reshape(na * na, len(vm)).T  # Matriz de señales agrupadas
    M1_df = pd.DataFrame(data=M1)
    f1 = pd.DataFrame(data=f * 10**6).to_numpy()
    
    # Guardando archivo CSV con señales y frecuencias
    output_filename = f'{n1}{edad}_agrupado{L}.csv'
    M1_df.to_csv(output_filename, index=False, header=False)
    print(f"Archivo guardado: {output_filename}")
    
    M1 = M1_df.to_numpy().astype(complex) 
    return M1, f1, M1.shape[0], M1.shape[1]

# Ejemplo de uso:
M1, f1, rows, cols = grouping('example', 4, '30', 'izquierda')
