#!/usr/bin/env python
# -*- coding: utf-8 -*-
import curses
import commands
import sys
import os
import argparse

# Variables en donde se guardara la informacion que se obtiene de ejecutar los comandos
global salida  
global num_lineas
global lista_salida
global remoto
global administrador


# Vamos a validar si tenemos acceso remoto a alguna de las cuentas de administrador
cuentas = commands.getoutput("cat ~/.ssh/config") 

if(cuentas.find("a.raco") != -1):
    administrador = "a.raco"
elif(cuentas.find("yoltla") != -1):
    administrador = "yoltla"
else:
    sys.stdout.write("NO CUENTAS CON ACCESO COMO ADMINISTRADOR\n")
    quit()

#En este metodo recuperaremos el nombre de todos los ususarios que tienen trabajos alojados en el servidor
def obtener_usuarios():
    #Consultamos todos los trabajos y capturamos en un string solo el nombre del usuario de cada trabajo 
    if(remoto == True):
        usuarios = commands.getoutput("ssh "+administrador+"squeue -h -o %u")
    else:
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
    
    return usuarios


#Validamos si recibimos el parametro -p para imprimir la informacion en la terminal
#si no se recibe el parametro entonces rescatamos la informacion para mostrarla con curses
def validar_opcion_p(salida):
	if(args.p):
		sys.stdout.write(salida+'\n')
		quit()
	else:
		num_lineas = str(len(salida.splitlines())-1)
		lista_salida = salida.splitlines()
	return num_lineas, lista_salida



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
    stdscr.addstr(0, 0, cabecera)
    stdscr.addstr(0, len(cabecera), " " * (width - len(cabecera)-1))
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

def validar_nodo(nodos):
    #Recuperamos el tercer caracter de la cadena para despues validar
    c = nodos[2]
    nodo = ""
    if(c == '['):
        #Si el tercer caracter de la cadena es [ entonces tenemos que
        # recuperar el nombre del primer nodo en base a la cadena 
        inicio = 3
        fin = len(nodos)
        nodo = nodos[:2]
        numero = ""
        for i in range(inicio, fin):
            caracter = nodos[i]
            if((caracter == '-') or (caracter == ',')):
                break
            else:
                numero += caracter
	#Tener precaucion con la identacion de esta linea, ya que asi como esta funciona bien para administrador, para usuario normal afecta al momento de recuperar el nombre del nodo 
	nodo += numero
    else:
        nodo = nodos
    return nodo

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


def obtener_variables_entorno(nodo):
	info_pstree = commands.getoutput("ssh " + nodo + " pstree -p | grep slurm_script")

	# Lista para almacenar los PIDs de info_pstree
	pids = []
	# Variables para indicar inicio y fin de PID
	inicio_pid = 0
	fin_pid = 0
	# indice para hacer referencia a la posicion del caracter de la cadena info_pstree
	indice = 0

	for c in info_pstree:
		if(c == '('):
			inicio_pid = indice + 1
		if( c == ')'):
			fin_pid = indice
		if( inicio_pid != 0 and fin_pid !=0):
			pids.append(info_pstree[inicio_pid:fin_pid])
			inicio_pid = 0
			fin_pid = 0
		indice = indice + 1
	# Recuperamos el PID del subproceso del cual recuperamos variables de entorno
	environ = commands.getoutput("ssh " + nodo + " strings /proc/" + pids[2] +"/environ")
	return environ


def desplegar_ayuda(stdscr):
	k = 0
	stdscr.clear()
	stdscr.refresh()
	height, width = stdscr.getmaxyx()
	ayuda_dict = {1: "Nota:", 2: "En esta version la ventana de la terminal no debe ser redimensionada durante la ejecucion de la aplicacion", 3: "q: ", 4: "Salir de la pantalla actual o salir del programa", 5: "h: ", 6: "Muestra esta pantalla de ayuda", 7: "R: ", 8: "Despliega la informacion de todos los trabajos que estan en ejecucion", 9: "P: ", 10: "Despliega la informacion de todos los trabajos pendientes", 11: "l: ", 12: "Despliega la informacion de todos los trabajos que estan alojados en el servidor", 13: "Enter: ", 14: "Permite visualizar informacion acerca del trabajo", 15: "w: ", 16: "Permite hacer una conexion por ssh al nodo y hacer top", 17: "e: ", 18: "Se contecta por ssh al nodo y ejecuta pstree con el usuaraio que esta utilizando el nodo", 19: "u: ", 20: "Muestra la informacion de todos los trabajos del usuario", 21: "p: ", 22:"Muestra la informacion de todos los trabajos pendientes del usuario", 23: "r: ", 24: "Muestra la informacion de todos los trabajos en enjecucion del usuario"}
	#Capturamos los datos del diccionario en una variable
	info_ayuda = ""
	for i in ayuda_dict:
		info_ayuda = info_ayuda + ayuda_dict[i]
    
	#Agregamos a la pantalla las lineas
	while (k != ord('q')):
		x = 0
		y = 0
		inicio = 0
		fin = 0
		for i in ayuda_dict:
			fin = fin + len(ayuda_dict[i])
			if(i%2 != 0):
				stdscr.attron(curses.color_pair(6))
				stdscr.addstr(y, 0, info_ayuda[inicio:fin])
				stdscr.attroff(curses.color_pair(6))
				x = len(ayuda_dict[i])
			else: 
				stdscr.attron(curses.color_pair(5))
				stdscr.addstr(y, x+1, info_ayuda[inicio:fin])
				stdscr.attroff(curses.color_pair(5))
				y = y + 2
			inicio = inicio + len(ayuda_dict[i])
		k = stdscr.getch()

def crear_subpantalla(stdscr, salida):
    k = 0 
    cursor_x = 0
    cursor_y = 1
    
    inicializar_curses(stdscr, cursor_y, cursor_x) 
    
    #info_barra_inf = {1:" q ",2:" Salir ",3:" Enter ", 4: " Conectar ", 5:" h ", 6:" Ayuda "}
    info_barra_inf = {1:" q ",2:" Salir ",3:" h ", 4:" Ayuda "}
    lista_salida = salida.splitlines()
    height, width = stdscr.getmaxyx()
    nlineasup = 1
    nlineainf = height - 1 #para tomar las lineas que podemos mostrar 
    inilinea = 0
    finlinea = width - 1
    
    while (k != ord('q')):
        desplegar_pantalla(stdscr, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida, info_barra_inf)
        # Esperamos a que se teclee una opcion
        k = stdscr.getch()
        if((k == curses.KEY_DOWN) or (k == curses.KEY_UP) or (k == curses.KEY_LEFT) or (k == curses.KEY_RIGHT) or (k == curses.KEY_NPAGE) or (k == curses.KEY_PPAGE) or (k == curses.KEY_RESIZE)):
            cursor_y, height, width, nlineasup, nlineainf, inilinea, finlinea= sroll(stdscr, k, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida)
        elif(k == ord('h')):
            desplegar_ayuda(stdscr)

def crear_pantalla_htop(stdscr, nodo):
    k = 0
    stdscr.clear()
    stdscr.refresh()
    
    while(k != ord('q')):
        os.system("ssh -t "+nodo+" top -id1")
        k = 113
    curses.endwin()

def crear_pantalla(stdscr):
    k = 0 
    cursor_x = 0
    cursor_y = 1
    global lista_salida
    global num_lineas
    global salida
    global remoto
    global administrador
    inicializar_curses(stdscr, cursor_y, cursor_x) 
    
    #Capturamos cada linea que contiene la variable salida en un arreglo
    height, width = stdscr.getmaxyx()
    nlineasup = 1
    nlineainf = height - 1 
    inilinea = 0
    finlinea = width - 1
    
    #Diccionario que contiene la informacion de teclas especiales
    info_barra_inf = {1:" q ",2:"Salir",3:" Enter ", 4: "Ver Trabajo", 5:" w ", 6:"Top", 7:" e ", 8:"pstree", 9:" u ", 10:"squeue -u", 11:" p ", 12:"squeue -tPD -u", 13:" r ", 14:"squeue -tR -u", 15:" R ", 16:"squeue -tR", 17:" P ", 18:"squeue -tPD", 19:" l ", 20:"squeue -l",21:" t ", 22:"less", 23:" h ", 24:"Ayuda"}
    while (k != ord('q')):
        desplegar_pantalla(stdscr, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida, info_barra_inf)
        k = stdscr.getch()
        if((k == curses.KEY_DOWN) or (k == curses.KEY_UP) or (k == curses.KEY_LEFT) or (k == curses.KEY_RIGHT) or (k == curses.KEY_NPAGE) or (k == 32) or (k == curses.KEY_PPAGE) or (k == curses.KEY_RESIZE)):
            cursor_y, height, width, nlineasup, nlineainf, inilinea, finlinea= sroll(stdscr, k, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida)
        elif(k == ord("\n")):
            """
            Queda pendiente validar esta funcion para su ejecucion de forma remota
            en esta version solo funciona en forma local como administrador
            """
            #Recuperamos la informacion de la linea en la que actualmente estael cursor
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            #Guardamos cada una de las cadenas que contiene la linea en un arreglo
            datos = linea.split()
            jobid = datos[-9]
            salida =  commands.getoutput("scontrol show jobid -dd  "+jobid)
            crear_subpantalla(stdscr, salida)
        elif(k == ord('w')):
            """
            Queda pendiente validar esta funcion para su ejecucion de forma remota
            en esta version solo funciona en forma local como administrador
            """
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos = linea.split()
            nodo = validar_nodo(datos[-1])
            crear_pantalla_htop(stdscr, nodo)
        elif(k == ord('e')):
            """
            Queda pendiente validar esta funcion para su ejecucion de forma remota
            en esta version solo funciona en forma local como administrador
            """
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos =  linea.split()
            usr = datos[-6]
            nodo = validar_nodo(datos[-1])
            salida = commands.getoutput("ssh "+nodo+" pstree -u "+usr+" -plac")
            crear_subpantalla(stdscr, salida)
        elif(k == ord('u')):
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos = linea.split()
            usuario = datos[-6]
            if(remoto == True):
                salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -u "+usuario)
            else:
                salida = commands.getoutput("python jobs.py -u "+usuario)
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
            cursor_x = 0
            cursor_y = 1
            height, width = stdscr.getmaxyx()
            nlineasup = 1
            nlineainf = height - 1 
            inilinea = 0
            finlinea = width - 1
        elif(k == ord('t')):
			user = os.getenv('USER')
			if(user == "root"):
				linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
				datos =  linea.split()
				nodo = validar_nodo(datos[-1])
				salida = obtener_variables_entorno(nodo)
				crear_subpantalla(stdscr, salida)
        elif(k == ord('r')):
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos = linea.split()
            usuario = datos[-6]
            if(remoto == True):
                salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -tR -u "+usuario)
            else:
                salida = commands.getoutput("python jobs.py -tR -u "+usuario)
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
            cursor_x = 0
            cursor_y = 1
            # Esto porque como es consulta probablemente el resultado sera de menos lineas por lo que vamos a reestablecer las variables
            # a sus valores de inicio para que no halla problema al momento de mostrar la informacion en pantalla 
            height, width = stdscr.getmaxyx()
            nlineasup = 1
            nlineainf = height - 1 
            inilinea = 0
            finlinea = width - 1
        elif(k == ord('R')):
            if(remoto == True):
                salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -tR")
            else:
                salida = commands.getoutput("python jobs.py -tR")
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
            cursor_x = 0
            cursor_y = 1
        elif(k == ord('p')):
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos = linea.split()
            usuario = datos[-6]
            if(remoto == True):
                salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -tPD -u "+usuario)
            else:
                salida = commands.getoutput("python jobs.py -tPD -u "+usuario)
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
            cursor_x = 0
            cursor_y = 1
            height, width = stdscr.getmaxyx()
            nlineasup = 1
            nlineainf = height - 1 
            inilinea = 0
            finlinea = width - 1
        elif(k == ord('P')):
            if(remoto == True):
                salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -tPD")
            else:
                salida = commands.getoutput("python jobs.py	-tPD ")
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
            cursor_x = 0
            cursor_y = 1
            # Esto porque como es consulta probablemente el resultado sera de menos lineas por lo que vamos a reestablecer las variables
            # a sus valores de inicio para que no halla problema al momento de mostrar la informacion en pantalla 
            height, width = stdscr.getmaxyx()
            nlineasup = 1
            nlineainf = height - 1 
            inilinea = 0
            finlinea = width - 1
        elif(k == ord('l')):
            usuarios = obtener_usuarios()
            if(remoto == True):
                salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py ")
            else:
                salida = commands.getoutput("python jobs.py -l")
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
            cursor_x = 0
            cursor_y = 1
            #Esto porque como es consulta probablemente el resultado sera de menos lineas por lo que vamos a reestablecer las variables
            #a sus valores de inicio para que no halla problema al momento de mostrar la informacion en pantalla 
            height, width = stdscr.getmaxyx()
            nlineasup = 1
            nlineainf = height - 1 
            inilinea = 0
            finlinea = width - 1
        elif(k == ord('h')):
            desplegar_ayuda(stdscr)



# Manejo de parametros que puede recibir al ejecutar el script
parser = argparse.ArgumentParser()
parser.add_argument("-R", action="store_true", help="Permite ejecutar este script de manera remota")
#parser.add_argument("-l", action="store_true", help="Muestra todos los trabajos")
parser.add_argument("-u", "--username", help="Muestra todos los trabajos del usuario <username>")
parser.add_argument("-tR", action="store_true", help="Muestra todos los trabajos en ejecucion")
parser.add_argument("-tPD", action="store_true", help="Muestra todos los trabajos pendientes")
parser.add_argument("-p", action="store_true", help="Imprime la informacion de los trabajos en la terminal")
parser.add_argument("-c", action="store_true", help="Imprime en terminal el numero de trabajos por usuario")

# Obtenemos los parametros que puede recibir el script
args = parser.parse_args()

# Validamos los casos posibles al recibir parametros para indicar que hacer en cada caso
#Validamos que parametros se recibieron para la ejecucion remota del script
if(args.R):
    remoto = True
    if(args.R and args.tR):
        if(args.username):
            salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -tR -u "+args.username)
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
        else: 
            salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -tR")
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
    elif(args.R and args.tPD):
        if(args.username):
            salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -tPD -u "+args.username)
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
        else:
            salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -tPD")
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
    elif(args.username):
        salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py -u "+args.username)
        num_lineas = str(len(salida.splitlines())-1)
        lista_salida = salida.splitlines()
    else:
        salida = commands.getoutput("ssh "+administrador+" python ./slurmwatch/jobs.py ")
        num_lineas = str(len(salida.splitlines())-1)
        lista_salida = salida.splitlines()
#Validamos las opciones recibidas en la ejecucion del script dentro de un  nodo en el cluster
else:
	remoto = False
	if(args.tR):
		if(args.username):
			salida = commands.getoutput("python jobs.py -tR -u "+args.username)
			num_lineas, lista_salida = validar_opcion_p(salida)
		else: 
			salida = commands.getoutput("python jobs.py -tR")
			num_lineas, lista_salida = validar_opcion_p(salida)
	elif(args.tPD):
		if(args.username):
			salida = commands.getoutput("python jobs.py -tPD -u "+args.username)
			num_lineas, lista_salida = validar_opcion_p(salida)
		else:
			salida = commands.getoutput("python jobs.py -tPD")
			num_lineas, lista_salida = validar_opcion_p(salida)
	elif(args.username):
		salida = commands.getoutput("python jobs.py -u "+args.username)
		num_lineas, lista_salida = validar_opcion_p(salida)
	elif(args.c):
		salida = commands.getoutput("python jobs.py -c")
		sys.stdout.write(salida+'\n')
		quit()
	else:
		salida = commands.getoutput("python jobs.py -l")
		num_lineas, lista_salida = validar_opcion_p(salida)

if(len(lista_salida) <= 1):
    ayuda = commands.getoutput("python slurmwatch.py -h")
    sys.stdout.write("Es necesario que agregues el parametro \"-R\" para ejecutar el script de manera remota"+'\n')
    sys.stdout.write('\n'+ayuda+'\n')
    quit()




def main():
    stdscr = curses.initscr()
    height, width = stdscr.getmaxyx()
    if(height >= 20 and width >= 116):
        curses.wrapper(crear_pantalla)
    else:
        if(height < 20 and width < 116):
            terminar()
            sys.stdout.write("Tamanio de pantalla insuficiente.....Renglones: "+str(height)+" Columnas: "+str(width)+"\nSe requiere minimo.....Renglones: 20 Columnas: 116"+'\n')
        if(height >= 20 and width < 116):
            terminar()
            sys.stdout.write("Tamanio de pantalla insuficiente.....Renglones: "+str(height)+" Columnas: "+str(width)+"\nSe requiere minimo.....Renglones: 20 Columnas: 116"+'\n')
        if(height < 20 and width >= 116):
            terminar()
            sys.stdout.write("Tamanio de pantalla insuficiente.....Renglones: "+str(height)+" Columnas: "+str(width)+"\nSe requiere minimo.....Renglones: 20 Columnas: 116"+'\n')

if __name__ == "__main__":
    #Capturamos la excepcion generada por Ctrl+C para terminar correctamente el programa
    try:
        main()
    except KeyboardInterrupt:
        terminar()
