import numpy as np
import pandas as pd
import math
from math import pi

def grouping(n1,na,edad,lado):
    M1 = [] #columnas(señales con tumor) agrupadas
    if lado == 'izquierda':
        Pos = 'A'
        L = 'Izq'
    elif lado == 'derecha':
        Pos = 'B'
        L = 'Der'
    for i in range(1,na+1):
        for j in range(1,na+1):
            name_file = 'datos/'+'resultsSOLT'+Pos+ '_p'+ str(i) + '_' + str(j)+ '.csv' ##definiendo archivo de lectura
            v=pd.read_csv(name_file,header = 0)##Leyendo csv de file vacio
            vm=v.iloc[:,0].values #mag
            vp=v.iloc[:,1].values #fase
            f=v.iloc[:,2].values #freq
            Sp=10** (vm/20) * np.exp(1j * vp * pi/180) # conversion fase a complejo
            
            for m in range(len(Sp)):   ## Agrupando señales y convirtiendo a str       
                if Sp[m].imag>=0: #M1
                    M1.append(str(Sp[m].real)+'+'+str(Sp[m].imag)+'j')
                else:
                    M1.append(str(Sp[m].real)+str(Sp[m].imag)+'j')
 
    M1=np.array(M1).reshape(na*na,len(vm)).T #matriz (señales en vacio) agrupadas
    M1=pd.DataFrame(data=M1)
    f1=pd.DataFrame(data=f).to_numpy()*10**6
    rows=np.shape(M1)[0]
    cols=np.shape(M1)[1]
    
    M1.to_csv(n1+edad+L+'_agrupado.csv',index=False,header=False) #guardando archivos S y Freq
    #f1.to_csv('Frequency_range_'+str(len(vm))+'.csv',index=False, header=False)
    
    M1=M1.to_numpy().astype(complex) 
    return M1,f1,rows,cols
