
import argparse
import sys
import commands
from operator import itemgetter




#Haremos uso de esta lista para poder almacenar la informacion de los trabajos
#Esta lista contendra elementos de tipo string para facilitar la impresion en pantalla
info = []


def imprimir_info(lista):
	"""
	En esta variable vamos a almacenar toda la informacion de los trabajos en 
	una sola cadena para poder hacer echo de esta variable mas adelante.
	"""
	aux  = ""
	for i in lista:
		aux += i+"\n"
	return aux
def imprime_trabajos(lista):
	for i in lista:
		renglon = commands.getoutput('echo '+"'"+i+"'"+' | column -t')
		print renglon
		


#Metodo que servira para poder agregar elementos a la lista info
def agregar_info(lista):
	
	for j in lista:
		lista_aux = []
		"""
		Hacemos la conversion de tipo int a tipo string para los primeros 4 elementos
		de la lista que contiene la informacion de los trabajos en ejecucion, ya que los primeros 
		4 elementos de esta lista son los valores asociados a CORES, INUSE, LOAD, %EFF
		"""
		lista_aux.append(str(j[0]))
		lista_aux.append(str(j[1]))
		lista_aux.append(str(j[2]))
		lista_aux.append(str(j[3]))
		
		lista_aux.extend(j[4:]) 
		
		cadena = " ".join(lista_aux)
		info.append(cadena)

def ajustar_output(output):
   
    #Quitamos los espacios en blanco que aparecen al principio de las cadenas
    
    valores = []
    
    for i in output:
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


def agregar_columnas_trabajos_ejecucion(output):
    cores = 0
    enuso = 0
    carga = 0
    eff = 0
    aux = []
    
    output = ajustar_output(output)
    
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


#Manejo de parametros que puede recibir el script
parser = argparse.ArgumentParser()
parser.add_argument("-u", help="Devulve informacion de los trabajos del/los usuarios")
parser.add_argument("-tR", action="store_true", help="Devuelve informacion de todos los trabajos en ejecucion")
parser.add_argument("-tPD", action="store_true", help="Devuelve informacion de todos los trabajos pendientes")
parser.add_argument("-l", action="store_true", help="Devuelve la informacion de todos los trabajos")

cabecera = "CORES INUSE LOAD %EFF JOBID PARTITION NAME USER STATE TIME TIME_LIMIT NODES NODELIST(REASON)"
info.append(cabecera)
ejecucion = []
pendientes = []

#obtenemos los parametros que puede recibir el script
args = parser.parse_args()

#Indicamos que realizar para cada parametro recibido
if(args.tR):
	if(args.u):
		ejecucion.extend((commands.getoutput("squeue -h -l -tR -u "+args.u)).splitlines())
	else:
		ejecucion.extend((commands.getoutput("squeue -h -l -tR")).splitlines())
	if(len(ejecucion) > 0):
		ejecucion = agregar_columnas_trabajos_ejecucion(ejecucion)
		agregar_info(ejecucion)
elif(args.tPD):
	if(args.u):
		pendientes.extend((commands.getoutput("squeue -h -l -tPD -u "+args.u)).splitlines())
	else:
		pendientes.extend((commands.getoutput("squeue -h -l -tPD")).splitlines())
	if(len(pendientes) > 0):
		pendientes = agregar_columnas_trabajos_pendientes(pendientes)
		agregar_info(pendientes)
elif(args.u):
	#Como todos los nombres de los usuarios los recibiremos en una cadena 
	#Los guardamos en una lista para solicitar la informacion de los trabajos de cada uno de ellos
	usuarios =  (args.u).split()

	for i in usuarios:
		ejecucion.extend((commands.getoutput("squeue -h -l -tR -u "+i)).splitlines())
		pendientes.extend((commands.getoutput("squeue -h -l -tPD -u "+i)).splitlines())

	if(len(ejecucion) > 0):
		ejecucion = agregar_columnas_trabajos_ejecucion(ejecucion)
		agregar_info(ejecucion)

	if(len(pendientes) > 0):
		pendientes = agregar_columnas_trabajos_pendientes(pendientes)
		agregar_info(pendientes)
elif(args.l):
	ejecucion.extend((commands.getoutput("squeue -h -l -tR")).splitlines())
	pendientes.extend((commands.getoutput("squeue -h -l -tPD")).splitlines())
	if(len(ejecucion) > 0):
		ejecucion = agregar_columnas_trabajos_ejecucion(ejecucion)
		agregar_info(ejecucion)
	if(len(pendientes) > 0):
		pendientes = agregar_columnas_trabajos_pendientes(pendientes)
		agregar_info(pendientes)
	
else:
	print "agregar parametro nombre de ususario"
	quit()


#imprime_trabajos(info)

informacion_trabajos = imprimir_info(info)
trabajos = commands.getoutput('echo '+"'"+informacion_trabajos+"'"+' | column -t')
print trabajos

