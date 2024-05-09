import pyvisa as visa #PyVisa es requerido junto con NIVISA
import csv #Importar libreria CSV para poder guardar los datos en ese formato
import numpy as np #Importar numpy para poder manejar los datos en forma de matriz
import serial #comunicacion con arduino
import time #tiempo de espera

def compute_barrido(lado):
    rm = visa.ResourceManager()
    #Conexion con socket 5025 en maquina local
    #Se utiliza la direccion IP de una maquina remota si es necesario en lugar de "localhost"
    try:
        CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
    except:
        print("Failure to connect to VNA!")
        print("Check network settings")
    #El VNA termina cada linea con este caracter. Las lecturas sobrepasarian el tiempo de timeout sin esto
    CMT.read_termination='\n'
    #Establecer un tiempo de timeout bastante largo para barridos lentos
    CMT.timeout = 100000

    ser=serial.Serial('COM4',9600)

    values = []
    CMT.write_ascii_values('MMEM:LOAD "4traces"\n',values) #Cargar el estado grabado previamente

    ##CMT.write_ascii_values('SENS1:FREQ:STAR 1 GHZ;STOP 8 GHZ\n',values)#Configurar limites de la ventana de muestra
    ##CMT.write_ascii_values('SENS1:BWID 10KHZ\n',values)#Configurar el ancho de banda
    ##CMT.write_ascii_values('SENS1:SWE:POIN 100\n',values) #Configurar el numero de muestras a tomar
    ##CMT.write_ascii_values('TRIG:SOUR BUS\n',values)#Configurar el inicio de la toma de muestras
    time.sleep(1)

    #cargamos el caso 0 todo apagado, esto nos da el valor del arduino
    #input('Presione Enter para comunicacion con el arduino')
    ser.write(str(0).encode())
    print('comunicacion con el arduino ')
    time.sleep(2)

    if lado == "Izquierdo":
        #Lado B
        count = 1
        
        for i in range(1, 9):
            for j in range(1, 9):

                ############
                print(i,j)

                time.sleep(1)
                ser.write(str(count).encode())  
                time.sleep(1)  
                #carga calibracion  
                CMT.write_ascii_values('MMEM:LOAD "A_1g_8g_10k_p'+str(i)+'_'+str(j)+'"\n',values) #Cargar la calibracion depende del puerto
                print('inicio del barrido S'+str(i)+'-'+str(j))
                npArray = barrido(CMT, values)

                with open('datos/resultsSOLTA_p'+str(i)+'_'+str(j)+'.csv', 'w',newline='') as csvFile: #Se guardan los datos en formato CSV
                    writer = csv.writer(csvFile)
                    writer.writerow(['S11m','S11p','S21m','S21p','Frequency'])
                    writer.writerows(npArray)
                    csvFile.close()
                ############
                count +=1

    elif lado == "Derecho":
        #Lado a
     
        count = 257

        for i in range(1, 9):
            for j in range(1, 9):

                ############
                print(i,j)

                time.sleep(1.5)
                ser.write(str(count).encode())  
                time.sleep(1.5)  
                #carga calibracion
                CMT.write_ascii_values('MMEM:LOAD "B_1g_8g_10k_p'+str(i)+'_'+str(j)+'"\n',values) #Cargar la calibracion depende del puerto
                print('inicio del barrido S'+str(i)+'-'+str(j))
                npArray = barrido(CMT, values)
                
                with open('datos/resultsSOLTB_p'+str(i)+'_'+str(j)+'.csv', 'w',newline='') as csvFile: #Se guardan los datos en formato CSV
                    writer = csv.writer(csvFile)
                    writer.writerow(['S11m','S11p','S21m','S21p','Frequency'])
                    writer.writerows(npArray)
                    csvFile.close()
                ############
                count +=1

def barrido(CMT, values):
            
    CMT.write_ascii_values('SENS1:FREQ:STAR 2 GHZ;STOP 7 GHZ\n',values)#Configurar limites de la ventana de muestra
    CMT.write_ascii_values('SENS1:BWID 1 KHZ\n',values)#Configurar IF Bandwith
    CMT.write_ascii_values('SENS1:SWE:POIN 501\n',values) #Configurar el numero de muestras a tomar
    CMT.write_ascii_values('SENS1:AVER 2\n',values) #Configurar el numero de muestras a tomar
    CMT.write_ascii_values('TRIG:SOUR BUS\n',values)#Configurar el inicio de la toma de muestras

    CMT.write_ascii_values('TRIG:SEQ:SING\n',values) #Iniciar un barrido
    CMT.query('*OPC?\n') #Esperar para que el barrido termine

    Freq = CMT.query("SENS1:FREQ:DATA?\n") #Obtener datos como una sequencia de caracteres
    S11m = CMT.query("CALC1:TRAC1:DATA:FDAT?\n")
    S21m = CMT.query("CALC1:TRAC2:DATA:FDAT?\n")
    S11p = CMT.query("CALC1:TRAC3:DATA:FDAT?\n")
    S21p = CMT.query("CALC1:TRAC4:DATA:FDAT?\n")

    #obtener la medición del marcador
    #M1 = CMT.query("CALC1:MARK1:Y?\n") #Obtener el valor en el marcador 1
    #M1 = M1.split(',') #Partir la sequencia de caracteres en una lista de 2 miembros

    #M1 = float(M1[0]) #COnvertir al primer miembro de la lista en un float

    #print('Marker 1 is ',M1,' dB') #Mostrar el valor del marcador 1

    #Partir la sequencia de caracteres en una lista
    #Tambien tomar cada otro valor de la magnitud
    #Si se usan datos complejos usariamos el formato polar y el segundo valor seria la parte imaginaria
    Freq = Freq.split(",")
    S11m = S11m.split(",")
    S11m = S11m[::2]
    S21m = S21m.split(",")
    S21m = S21m[::2]

    S11p = S11p.split(",")
    S11p = S11p[::2]
    S21p = S21p.split(",")
    S21p = S21p[::2]
    #Convertir los caracteres en numeros float
    S11m = [float(s) for s in S11m]
    S21m = [float(s) for s in S21m]
    Freq = [float(f)/1e6 for f in Freq]
    S11p = [float(s) for s in S11p]
    S21p = [float(s) for s in S21p]

    #Para obtener los datos en formato CSV donde cada columna es un parametro y la columna final es la frecuencia
    #global npArray
    npArray=np.array([S11m,S11p,S21m,S21p,Freq]) #Se unen los datos en forma de matriz
    npArray=npArray.transpose() #Se realiza una transpuesta de la matriz para que los datos esten en columnas
    return npArray
