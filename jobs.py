import sys
import commands
from operator import itemgetter


def imprimir(lista):
    for i in lista:
        print i



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
    #print output

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

    #REcuperamos solo la parte numerica de CPUAlloc, CPUTot, CPULoad
    for i in valores_load:
        Cores += int(i[2].lstrip(secuencia1))
        Usados += int(i[0].lstrip(secuencia2))
        Carga += float(i[3].lstrip(secuencia3))

    Eff = (Carga/Usados)*100
    #print "Cores: "+str(Cores)+" Usados: "+str(Usados)+" Carga: "+str(Carga)+" %Eff: "+str(int(Eff))
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


def agregar_colum_output(output):
    cores = 0
    enuso = 0
    carga = 0
    eff = 0
    aux = []
    espcores = 0
    espuso = 0
    espcarga = 0
    espeff = 0
    espmaxcores = 3
    espmaxenuso = 3
    espmaxcarga = 6
    espmaxeff = 3
    
    for i in output:
        nodos = i.split()[-1]
        cores, enuso, carga, eff = obtener_carga(nodos)
        len_cores = len(str(cores))
        len_enuso = len(str(enuso))
        len_carga = len(str(carga))
        len_eff = len(str(eff))
        if(len_cores < espmaxcores ):
            espcores = espmaxcores - len_cores
        else: 
            espcores = 0
        if(len_enuso < espmaxenuso):
            espuso = espmaxenuso - len_enuso
        else:
            espuso = 0
        if(len_carga < espmaxcarga):
            espcarga = espmaxcarga - len_carga
        else:
            espcarga = 0
        if(len_eff < espmaxeff):
            espeff = espmaxeff - len_eff
        else:
            espeff = 0
        i = str(cores)+espcores*" "+ "    "+str(enuso)+espuso*" "+"    "+str(carga)+espcarga*" "+"    "+str(eff)+espeff*" "+"    "+i 
        aux.append(i.split())


    return aux





cabecera = "CORES INUSE LOAD  %EFF  JOBID       PARTITION   NAME        USER        STATE     TIME        TIME_LIMI   NODES NODELIST(REASON)"
#cabecera = "CORES INUSE LOAD  %EFF  JOBID     PARTITION     NAME       USER         ST TIME     NODES NODELIST(REASON)"
usuario = ""
if(len(sys.argv)>1):
    usuario = sys.argv[1]    
    output = commands.getoutput("squeue -h -l -tR -u "+usuario)
else:
    output = commands.getoutput("squeue -h -l -tR")

output = ajustar_output(output)
output = agregar_columns_output(output)

print cabecera
for j in output:
    cadena = "%-6s%-6s%-6s%-6s%-12s%-12s%-12s%-12s%-10s%-12s%-13s%-5s%-12s" %  (str(j[0]), str(j[1]), str(j[2]), str(j[3]), j[4], j[5], j[6], j[7], j[8], j[9], j[10], j[11],j[12])  
    print cadena

