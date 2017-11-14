
import argparse
import sys
import commands
from operator import itemgetter
import time



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
		aux += i+'\n' 
	return aux

def imprime_trabajos(lista):
	for j in lista:
		cadena = "%-6s%-6s%-6s%-6s%-12s%-12s%-12s%-10s%-10s%-12s%-13s%-6s%-12s" %  (j[0], j[1], j[2], j[3], j[4], j[5], j[6], j[7], j[8], j[9], j[10], j[11],j[12])
		print cadena
		#print('{0:5s} {1:5s} {2:4s} {3:4s} {4:16s} {5:12s} {6:12s} {7:10s} {8:8s} {9:10s} {10:5s} {11:s}'.format(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11]))
		
def ajustar_trabajos_por_usuario(lista):
	trabajos_por_usuario = ""

	for i in lista:
		informacion = " ".join(i)
		trabajos_por_usuario += informacion+"\n"
	return trabajos_por_usuario

def imprimir_trabajos_por_usuario(lista):
	informacion_trabajos = ajustar_trabajos_por_usuario(lista)
	trabajos_por_usuario = commands.getoutput('echo '+"'"+informacion_trabajos+"'"+' | column -t')
	print trabajos_por_usuario

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
		
		#cadena = " ".join(lista_aux)
		#info.append(cadena)
		info.append(lista_aux)

def agregar_pendientes(pendientes):
	lista_aux = []
	for i in pendientes:
		cadena = " ".join(i)
		lista_aux.append(cadena)
	info.extend(lista_aux)

	

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

def validar_trabajos_ejecucion(ejecucion):
	if(len(ejecucion) > 0):
		ejecucion = agregar_columnas_trabajos_ejecucion(ejecucion)
		agregar_info(ejecucion)


def agregar_columnas_trabajos_pendientes(pendientes):
    pendientes = ajustar_output(pendientes)
    aux = []
    for i in pendientes:
		valores_i = i.split()
		columnas = ["---", "---", "---", "---"]
		columnas.extend(valores_i)
		aux.append(columnas)
    return aux

def validar_trabajos_pendientes(pendientes):
	if(len(pendientes) > 0):
		pendientes = agregar_columnas_trabajos_pendientes(pendientes)
		agregar_info(pendientes)


def obtener_usuarios():
 	#Consultamos todos los trabajos y capturamos en un string solo el nombre del usuario de cada trabajo 
	usuarios = commands.getoutput("squeue -h -o %u")
    #A partir del string usuarios creamos una lista que contiene cada uno de los nombres de usuario, habra nombres de usuarios repetidos 
	lista_usuarios = usuarios.splitlines()
		
	#Diccionario que ocuparemos para almacenar los nombres de usuario sin nombres de usuario repetidos
	dict_usuarios = {}
	#A continuacion agregamos nombres de usuario a dic_usuarios, aseguramos que no halla nombres de usuario repetidos
	#Y recuperamos los nombres de los usuarios en una lista 
	usuarios_aux = [dict_usuarios.setdefault(x,x) for x in lista_usuarios if x not in dict_usuarios]	
	#Recuperamos todos los nombres de usuario en una cadena
	usuarios = " ".join(usuarios_aux)
	
	return usuarios_aux


def trabajos_por_usuario():
	usuarios = obtener_usuarios()
	cabecera = ["uSER", "RUNNING", "PENDING"]
	informacion = []
	informacion.append(cabecera)

	ejecucion = commands.getoutput("squeue -h -tR -o %u")
	pendientes = commands.getoutput("squeue -h -tPD -o %u")

	for usr in usuarios:
		trabajos_por_usuario = []
		num_trabajos_ejecucion = ejecucion.count(usr)
		num_trabajos_pendientes = pendientes.count(usr)
		
		trabajos_por_usuario.append(usr)
		trabajos_por_usuario.append(str(num_trabajos_ejecucion))
		trabajos_por_usuario.append(str(num_trabajos_pendientes))
		
		informacion.append(trabajos_por_usuario)
	
	return informacion


#Manejo de parametros que puede recibir el script
parser = argparse.ArgumentParser()
parser.add_argument("-u", help="Devulve informacion de los trabajos del/los usuarios")
parser.add_argument("-tR", action="store_true", help="Devuelve informacion de todos los trabajos en ejecucion")
parser.add_argument("-tPD", action="store_true", help="Devuelve informacion de todos los trabajos pendientes")
parser.add_argument("-l", action="store_true", help="Devuelve la informacion de todos los trabajos")
parser.add_argument("-c", action="store_true", help="Devuelve la cantidad de trabajos alojados que tiene cada uno de los usuarios")

#cabecera = "CORES INUSE LOAD %EFF JOBID PARTITION NAME USER STATE TIME TIME_LIMIT NODES NODELIST(REASON)"
cabecera = ["CORES","INUSE","LOAD","%EFF","JOBID","PARTITION","NAME","USER","STATE","TIME","TIME_LIMIT","NODES","NODELIST(REASON)"]
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

	validar_trabajos_ejecucion(ejecucion)
	imprime_trabajos(info)
elif(args.tPD):
	if(args.u):
		pendientes.extend((commands.getoutput("squeue -h -l -tPD -u "+args.u)).splitlines())
	else:
		pendientes.extend((commands.getoutput("squeue -h -l -tPD")).splitlines())
		#pendientes.extend((commands.getoutput("squeue -h -l -tPD")).splitlines())

	validar_trabajos_pendientes(pendientes)
	imprime_trabajos(info)
elif(args.u):
	#Como todos los nombres de los usuarios los recibiremos en una cadena 
	#Los guardamos en una lista para solicitar la informacion de los trabajos de cada uno de ellos
	usuarios =  (args.u).split()

	for i in usuarios:
		ejecucion.extend((commands.getoutput("squeue -h -l -tR -u "+i)).splitlines())
		pendientes.extend((commands.getoutput("squeue -h -l -tPD -u "+i)).splitlines())

	validar_trabajos_ejecucion(ejecucion)
	validar_trabajos_pendientes(pendientes)
	imprime_trabajos(info)
elif(args.l):
	ejecucion.extend((commands.getoutput("squeue -h -l -tR")).splitlines())
	pendientes.extend((commands.getoutput("squeue -h -l -tPD")).splitlines())
	
	validar_trabajos_ejecucion(ejecucion)
	validar_trabajos_pendientes(pendientes)
	imprime_trabajos(info)
elif(args.c):
	imprimir_trabajos_por_usuario(trabajos_por_usuario())

else:
	print "agregar parametro nombre de ususario"
	quit()


#imprime_trabajos(info)
#if(len(ejecucion) > 0):
	#ejecucion = agregar_columnas_trabajos_ejecucion(ejecucion)
	#agregar_info(ejecucion)
	#informacion_trabajos = imprimir_info(info)
	#print informacion_trabajos
	#time.sleep(3)
#if(len(pendientes) > 0):
	#pendientes = agregar_columnas_trabajos_pendientes(pendientes)
	#agregar_info(pendientes)
	#informacion_trabajos = imprimir_info(info)
	#print informacion_trabajos
	#agregar_pendientes(pendientes)
	#imprime_trabajos(pendientes)
	#agregar_pendientes(pendientes)

#imprime_trabajos(info)
#imprime_trabajos(info)
#informacion_trabajos = imprimir_info(info)
#print informacion_trabajos
#trabajos = commands.getoutput('echo '+"'"+informacion_trabajos+"'"+' | column -t')
#print trabajos
#sys.stdout.write(trabajos+'\n')

