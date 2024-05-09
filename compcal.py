import fileinput
import sys

traza = "TraceCount=4" #columnas(señales con tumor) agrupadas

Pos='B'
na=8

def modificarLinea(archivo,buscar,reemplazar):
	"""
	Esta simple función cambia una linea entera de un archivo
	Tiene que recibir el nombre del archivo, la cadena de la linea entera a
	buscar, y la cadena a reemplazar si la linea coincide con buscar
	"""
 
	with open(archivo, "r") as f:
		# obtenemos las lineas del archivo en una lista
		lines = (line.rstrip() for line in f)
 
		# busca en cada linea si existe la cadena a buscar, y si la encuentra
		# la reemplaza
		altered_lines = [reemplazar if line==buscar else line for line in lines]
 
	with open(archivo, "w") as f:
		# guarda nuevamente todas las lineas en el archivo
		f.write('\n'.join(altered_lines) + '\n')
 


var1 = "CorrectionEnabled=1\n"
var2 = "CorrectionEnabled=1\nTraceCount=4"

for i in range(1,na+1):
        for j in range(1,na+1):
            name_file = 'State/' + 'COOPER_SOLT_'+Pos+ '_1g_8g_10k_p'+ str(i) + '_' + str(j)+ '.sta' ##definiendo archivo de lectura
            modificarLinea(name_file,var1,var2)
    
