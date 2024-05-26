import pyvisa as visa
import csv
import numpy as np
import serial
import time

def compute_barrido(lado):
    rm = visa.ResourceManager()
    try:
        CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
    except Exception as e:
        print("Error al conectar con el VNA:", e)
        return

    CMT.read_termination = '\n'
    CMT.timeout = 100000

    try:
        ser = serial.Serial('COM4', 9600)
    except serial.SerialException as e:
        print("No se puede abrir el puerto serial:", e)
        return

    values = []
    CMT.write_ascii_values('MMEM:LOAD "4traces"\n', values)
    time.sleep(1)

    ser.write(str(0).encode())
    print('Comunicación con el Arduino')
    time.sleep(2)

    if lado == "izquierda":
        count = 1
        for i in range(1, 9):
            for j in range(1, 9):
                print(i, j)
                time.sleep(3)
                ser.write(str(count).encode())
                time.sleep(3)
                CMT.write_ascii_values(f'MMEM:LOAD "A_1g_8g_10k_p{i}_{j}"\n', values)
                print(f'Inicio del barrido S{i}-{j}')
                npArray = barrido(CMT, values)
                filename = f'datos/resultsSOLTA_p{i}_{j}.csv'
                with open(filename, 'w', newline='') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(['S11m', 'S11p', 'S21m', 'S21p', 'Frequency'])
                    writer.writerows(npArray)
                print(f'Resultados guardados en {filename}')
                count += 1

    elif lado == "derecha":
        count = 257
        for i in range(1, 9):
            for j in range(1, 9):
                print(i, j)
                time.sleep(1.5)
                ser.write(str(count).encode())
                time.sleep(1.5)
                CMT.write_ascii_values(f'MMEM:LOAD "B_1g_8g_10k_p{i}_{j}"\n', values)
                print(f'Inicio del barrido S{i}-{j}')
                npArray = barrido(CMT, values)
                filename = f'datos/resultsSOLTB_p{i}_{j}.csv'
                with open(filename, 'w', newline='') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(['S11m', 'S11p', 'S21m', 'S21p', 'Frequency'])
                    writer.writerows(npArray)
                print(f'Resultados guardados en {filename}')
                count += 1

def barrido(CMT, values):
    CMT.write_ascii_values('SENS1:FREQ:STAR 2 GHZ;STOP 7 GHZ\n', values)
    CMT.write_ascii_values('SENS1:BWID 1 KHZ\n', values)
    CMT.write_ascii_values('SENS1:SWE:POIN 501\n', values)
    CMT.write_ascii_values('SENS1:AVER 2\n', values)
    CMT.write_ascii_values('TRIG:SOUR BUS\n', values)
    CMT.write_ascii_values('TRIG:SEQ:SING\n', values)
    CMT.query('*OPC?\n')

    Freq = CMT.query("SENS1:FREQ:DATA?\n")
    S11m = CMT.query("CALC1:TRAC1:DATA:FDAT?\n")
    S21m = CMT.query("CALC1:TRAC2:DATA:FDAT?\n")
    S11p = CMT.query("CALC1:TRAC3:DATA:FDAT?\n")
    S21p = CMT.query("CALC1:TRAC4:DATA:FDAT?\n")

    Freq = Freq.split(",")
    S11m = S11m.split(",")[::2]
    S21m = S21m.split(",")[::2]
    S11p = S11p.split(",")[::2]
    S21p = S21p.split(",")[::2]

    S11m = [float(s) for s in S11m]
    S21m = [float(s) for s in S21m]
    Freq = [float(f) / 1e6 for f in Freq]
    S11p = [float(s) for s in S11p]
    S21p = [float(s) for s in S21p]

    npArray = np.array([S11m, S11p, S21m, S21p, Freq]).T
    return npArray
