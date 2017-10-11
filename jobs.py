import sys
import commands
from operator import itemgetter


def imprimir(lista):
    for j in lista:
        cadena = "%-6s%-6s%-6s%-6s%-14s%-12s%-12s%-12s%-10s%-12s%-13s%-5s%-12s" %  (str(j[0]), str(j[1]), str(j[2]), str(j[3]), j[4], j[5], j[6], j[7], j[8], j[9], j[10], j[11],j[12])  
        print cadena

def ajustar_output(output):
   
    #Quitamos los espacios en blanco que aparecen al principio de las cadenas
    
    valorestemp = output.splitlines()
    valores = []
    
    for i in valorestemp:
        i = i.strip()
        valores.append(i)
    return valores

def obtener_carga(nodes):

    output = commands.getoutput("scontrol show nodes "+nodes+" | grep CPULoad")
    valores_loadtemp = output.splitlines()

    valores_load = []
    #Guardamos en una lista la lista que contiene los valores de CPUAlloc, CPUTot, CPULoad
    for i in valores_loadtemp:
        valores_load.append(i.split())
    
    Cores = 0
    Usados = 0
    Carga = 0
    Eff = 0
    secuencia1 = "CPUTot="
    secuencia2 = "CPUAlloc="
    secuencia3 = "CPULoad="

    #Recuperamos solo la parte numerica de CPUAlloc, CPUTot, CPULoad
    for i in valores_load:
        Cores += int(i[2].lstrip(secuencia1))
        Usados += int(i[0].lstrip(secuencia2))
        Carga += float(i[3].lstrip(secuencia3))
    if(Usados != 0):
    	Eff = (Carga/Usados)*100
    else:
	Eff = 0
    return Cores, Usados,int(Carga), int(Eff)


def agregar_columns_output(output):
    cores = 0
    enuso = 0
    carga = 0
    eff = 0
    aux = []
    auxfin = []
    for i in output:
        valores = []
        valores_output = i.split()
        nodos = valores_output[-1]
        cores, enuso, carga, eff = obtener_carga(nodos)
        valores.append(cores)
        valores.append(enuso)
        valores.append(carga)
        valores.append(eff)
        valores.extend(valores_output)
	
	aux.append(valores)
	
    aux.sort(key=itemgetter(3), reverse=True)
    return aux

def agregar_columnas_trabajos_pendientes(pendientes):
    pendientes = ajustar_output(pendientes)
    aux = []
    for i in pendientes:
	valores_i = i.split()
        columnas = ["---", "---", "---", "---"]
        columnas.extend(valores_i)
	aux.append(columnas)
    return aux


cabecera = "CORES INUSE LOAD  %EFF  JOBID         PARTITION   NAME        USER        STATE     TIME        TIME_LIMI   NODES NODELIST(REASON)"

usuario = sys.argv[1]    
output = commands.getoutput("squeue -h -l -tR -u "+usuario)
pendientes = commands.getoutput("squeue -h -l -tPD -u "+usuario)


print cabecera

if(len(output.splitlines()) > 0):
	output = ajustar_output(output)
	output = agregar_columns_output(output)
	imprimir(output)
if(len(pendientes.splitlines()) > 0):
	pendientes = agregar_columnas_trabajos_pendientes(pendientes)
        imprimir(pendientes)

