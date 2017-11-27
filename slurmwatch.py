# -*- coding: utf-8 -*-
#!/usr/bin/env python
import curses
import commands
import sys
import os
import argparse
from operator import itemgetter


# Variables en donde se guardara la informacion que se obtiene de ejecutar los comandos
global salida  
global num_lineas
global lista_salida
#Haremos uso de esta lista para poder almacenar la informacion de los trabajos
#Esta lista contendra elementos de tipo string para facilitar la impresion en pantalla
info = []

# Con esta funcion almacenamos todo en una variable para despues hacer echo y aplicar column -t para que se haga de mejor manera la tabulacion
# Falta validar bien ya que de momento se rebasa el limite de caracteres aceptados por echo y al final imprime una linea en blanco
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
	informacion = ""
	for j in lista:
		cadena = "%-6s%-6s%-6s%-6s%-12s%-12s%-12s%-10s%-10s%-12s%-13s%-6s%-12s" %  (j[0], j[1], j[2], j[3], j[4], j[5], j[6], j[7], j[8], j[9], j[10], j[11],j[12])
		informacion +=cadena+"\n"
	return informacion

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

		info.append(lista_aux)
		#Esto solo para que funcione al momento de hacer echo de la cadena para obtener mejor tabulacion
		#cadena = " ".join(lista_aux)
		#info.append(cadena)

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

def consultar_trabajos(usuario):
	
	#Esta variable es util para cuando hacemos echo y column -t 
	#cabecera = "CORES INUSE LOAD %EFF JOBID PARTITION NAME USER STATE TIME TIME_LIMIT NODES NODELIST(REASON)"
	cabecera = ["CORES","INUSE","LOAD","%EFF","JOBID","PARTITION","NAME","USER","STATE","TIME","TIME_LIMIT","NODES","NODELIST(REASON)"]
	info.append(cabecera)
	informacion_trabajos = ""
	usuarios = usuario.split()
	ejecucion = []
	pendientes = []

	for i in usuarios:
		ejecucion.extend((commands.getoutput("squeue -h -l -tR -u "+i)).splitlines())
		pendientes.extend((commands.getoutput("squeue -h -l -tPD -u "+i)).splitlines())
	
	if(len(ejecucion) > 0):
		ejecucion = agregar_columnas_trabajos_ejecucion(ejecucion)
		agregar_info(ejecucion)

	if(len(pendientes) > 0):
		pendientes = agregar_columnas_trabajos_pendientes(pendientes)
		agregar_info(pendientes)

	if(len(info) > 1):
		informacion_trabajos = imprime_trabajos(info)
	return informacion_trabajos




def validar_usuario_investigador(usuario, user_id):
	usuarios = " "
	id_inferior = 5000
	id_superior = 6000
	if((id_inferior < user_id) and (user_id < id_superior)):
		info_user = commands.getoutput("cat /etc/passwd | grep "+usuario+" | awk '{ print $1 }'")
		info_user = info_user.split()
		users = []
		for i in info_user:
			aux = i.split(":")
			users.append(aux[0])
		usuarios = " ".join(users)
		sys.stdout.write(usuarios+'\n')
	else:
		usuarios = usuario
	return usuarios


def inicializar_curses(stdscr, cursor_y, cursor_x):

    height, width = stdscr.getmaxyx()

    #Ocultamos el cursor
    curses.curs_set(0)

    #Inicilaizamos los colores
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)


    #Definimos limites para mover el cursor  
    cursor_x = max(0, cursor_x)
    cursor_x = min(width-1, cursor_x)

    cursor_y = max(0, cursor_y)
    cursor_y = min(height-1, cursor_y)


def sroll(stdscr, k, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida): 
    if k == curses.KEY_DOWN:
        if(cursor_y < height - 2):
            if(cursor_y != len(lista_salida) -1):
                cursor_y = cursor_y + 1
        else:
            if(nlineainf != len(lista_salida)): 
                nlineasup = nlineasup + 1
                nlineainf = nlineainf + 1
        
    elif k == curses.KEY_UP:
        if(cursor_y > 1 and  cursor_y < height - 1):
            cursor_y = cursor_y - 1
        else:
            if(nlineasup!=1):     
                nlineasup = nlineasup - 1
                nlineainf = nlineainf - 1
    elif k == curses.KEY_RIGHT:
        #cursor_x = cursor_x + 1
        inilinea += 1
        finlinea += 1
    elif k == curses.KEY_LEFT:
        if (inilinea > 0 and finlinea >= width ):
            inilinea -= 1
            finlinea -= 1

       #cursor_x = cursor_x - 1
    elif((k == curses.KEY_NPAGE) or (k == 32)):
        if(nlineainf < len(lista_salida)):
            if(nlineasup < nlineainf):
                nlineasup = nlineainf
                nlineainf += (height - 2)
                aux = lista_salida[nlineasup:nlineainf]
                if(len(aux) < (height - 2)):
                    nlineasup = len(lista_salida) - (height -2)
                    nlineainf = len(lista_salida)
    elif(k == curses.KEY_PPAGE):
        if(nlineasup > 1):
            if(nlineasup < nlineainf):
                nlineainf = nlineasup
                nlineasup -= (height -2)
                aux = lista_salida[nlineasup:nlineainf]
                if(len(aux) < (height - 2)):
                    nlineasup = 1
                    nlineainf = height -1
    elif k == curses.KEY_RESIZE:
        #Validamos si han redimensionado la terminal para reajustar las informacion en la pantalla
        #Aun hay detalles minimos para mejorar el control de la redimension
        heightact, widthact = stdscr.getmaxyx()
        aux = widthact - width
        finlinea += aux
        width = widthact
        if nlineasup == 0:
            nlineainf = heightact - 1
            #lineas = (heightact - height)
            height = heightact
        else:
            lineas = (heightact - height)
            if(cursor_y == height - 2 and lineas < 0):
                cursor_y = heightact - 2
                nlineainf += lineas
                stdscr.move(cursor_y, cursor_x)
                #stdscr.refresh()
            else:
                if nlineainf < len(lista_salida):
                    nlineainf += lineas
                else:
                    nlineainf = len(lista_salida)
                    
            aux = lista_salida[nlineasup:nlineainf]
            if(len(aux) < (heightact- 2)):
                nlineasup = len(lista_salida) - (heightact - 2)
                nlineainf = len(lista_salida)
            height = heightact
    return cursor_y, height, width, nlineasup, nlineainf, inilinea, finlinea


    


def desplegar_pantalla(stdscr, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida, info_barra_inf):
    #height, width = stdscr.getmaxyx()
    nlinea = 1
    stdscr.clear()
    stdscr.refresh()
         
    lineas_en_pantalla = lista_salida[nlineasup:nlineainf]
    
    #Agregamos la cabecera a la pantalla
    cabecera = lista_salida[0]
    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(0, 0, cabecera[inilinea:finlinea])
    stdscr.addstr(0, len(cabecera[inilinea:finlinea]), " " * (width - len(cabecera[inilinea:finlinea])-1))
    stdscr.attroff(curses.color_pair(3))
    #Capturamos los datos del diccionario en una variable
    barra = ""
    for i in info_barra_inf:
        barra = barra + info_barra_inf[i]
    
    #Agregamos la ultima linea de la pantalla que contiene informacion
    #sobre las teclas especiales
    inicio = 0
    fin = 0    
    for i in info_barra_inf:
        fin = fin + len(info_barra_inf[i])
        if(i%2 != 0):
            stdscr.attron(curses.color_pair(2))
            stdscr.addstr(height-1, inicio, barra[inicio:fin])
            stdscr.attroff(curses.color_pair(2))
        else: 
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(height-1, inicio, barra[inicio:fin])
            stdscr.attroff(curses.color_pair(3))
                
        if(i == len(info_barra_inf)):
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(height-1, len(barra), " " * (width - len(barra)-1-len(num_lineas)))
            stdscr.attroff(curses.color_pair(3))
        
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(height-1, width - len(num_lineas)-1, num_lineas)
            stdscr.attroff(curses.color_pair(1))
            
        inicio = inicio + len(info_barra_inf[i])
   

    if(height > len(lineas_en_pantalla)): 
        for i in lineas_en_pantalla:
            stdscr.addstr(nlinea, 0, i[inilinea:finlinea])
            nlinea = nlinea + 1
    else:
        
        for i in lineas_en_pantalla:
            stdscr.addstr(nlinea, 0,i[inilinea:finlinea])
            nlinea = nlinea + 1
            if(nlinea == height-1):
                nlineainf = height - 1 
                break
   
    #Establecemos el fondo de la linea en donde actualmente esta el cursor 
    linea = obtener_linea(lineas_en_pantalla, cursor_y)
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(cursor_y, 0, linea[inilinea:finlinea])
    if(len(linea[inilinea:finlinea]) <= width):
        stdscr.addstr(cursor_y, len(linea[inilinea:finlinea]), " " * (width - len(linea[inilinea:finlinea])-1))
    else:
        stdscr.addstr(cursor_y, 0," " * (width - 1)) 
    stdscr.attroff(curses.color_pair(1))
    
    stdscr.move(cursor_y, cursor_x)
    stdscr.refresh()       
    

def terminar():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def obtener_linea(list_salida, no_linea):
    contador = 1
    linea = " "
    for i in list_salida: 
        if(contador == no_linea):
            linea = i
        contador = contador + 1
    return linea

def recuperar_linea(lista_salida, no_linea, nlineasup, nlineainf):
    contador = 1
    linea = " "
    for i in range(nlineasup,nlineainf):
        if(contador == no_linea):
            linea = lista_salida[i]
        contador = contador + 1
    return linea


def crear_pantalla(stdscr):
    k = 0 
    cursor_x = 0
    cursor_y = 1
    global lista_salida
    global num_lineas
    global salida
    inicializar_curses(stdscr, cursor_y, cursor_x) 
    
    #Capturamos cada linea que contiene la variable salida en un arreglo
    height, width = stdscr.getmaxyx()
    nlineasup = 1
    nlineainf = height - 1 
    inilinea = 0
    finlinea = width - 1

    #Diccionario que contiene la informacion de teclas especiales
    info_barra_inf = {1:" q ",2:"Salir"}
    
    while (k != ord('q')):

        desplegar_pantalla(stdscr, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida, info_barra_inf)
        
        k = stdscr.getch()
        if((k == curses.KEY_DOWN) or (k == curses.KEY_UP) or (k == curses.KEY_LEFT) or (k == curses.KEY_RIGHT) or (k == curses.KEY_NPAGE) or (k == 32) or (k == curses.KEY_PPAGE) or (k == curses.KEY_RESIZE)):
            cursor_y, height, width, nlineasup, nlineainf, inilinea, finlinea= sroll(stdscr, k, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida)


 
# Manejo de parametros que puede recibir al ejecutar el script
parser = argparse.ArgumentParser()
parser.add_argument("-A", action="store_true", help="Muestra informacion de trabajos del usuario, colaboradores y alumnos")
parser.add_argument("-p", action="store_true", help="Imprime la informacion de los trabajos en la terminal")

# Obtenemos los parametros que puede recibir el script
args = parser.parse_args()

# Validamos los casos posibles al recibir parametros para indicar que hacer en cada caso

if(args.A):
	usuario = os.getenv('USER')
	user_id = int(os.getuid())
	usuarios = validar_usuario_investigador(usuario, user_id)
	if(args.p):
		trabajos = consultar_trabajos(usuarios)
		sys.stdout.write(trabajos+"\n")
		quit()
	else:
		trabajos = consultar_trabajos(usuarios)
		lista_salida = trabajos.splitlines()
		num_lineas = str(len(lista_salida) - 1)
elif(args.p):
	usuario = os.getenv('USER')
	trabajos = consultar_trabajos(usuario)
	sys.stdout.write(trabajos)
	quit()
else:
	usuario = os.getenv('USER')
	trabajos = consultar_trabajos(usuario)
	lista_salida = trabajos.splitlines()
	num_lineas = str(len(lista_salida) - 1)

if(len(lista_salida) == 0):
	quit()



def main():
	stdscr = curses.initscr()
	height, width = stdscr.getmaxyx()
	terminar()
	sys.stdout.write("alto " +str(height)+" ancho "+str(width)+"\n")
	if(height >= 20 and width >= 129):
		curses.wrapper(crear_pantalla)
	else:
		if(height < 20 and width < 129):
			terminar()
			sys.stdout.write("Tamanio de pantalla insuficiente.....Renglones: "+str(height)+" Columnas: "+str(width)+"\nSe requiere minimo.....Renglones: 20 Columnas: 129"+'\n')
		if(height >= 20 and width < 129):
			terminar()
			sys.stdout.write("Tamanio de pantalla insuficiente.....Renglones: "+str(height)+" Columnas: "+str(width)+"\nSe requiere minimo.....Renglones: 20 Columnas: 129"+'\n')
		if(height < 20 and width >= 129):
			terminar()
			sys.stdout.write("Tamanio de pantalla insuficiente.....Renglones: "+str(height)+" Columnas: "+str(width)+"\nSe requiere minimo.....Renglones: 20 Columnas: 129"+'\n')

if __name__ == "__main__":
	"""
	Destectamos cuando usuario presona C-c y terminamos el programa
	"""
	try:
		main()
	except KeyboardInterrupt:
		terminar()

