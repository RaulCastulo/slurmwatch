#!/usr/bin/env python
import curses
import commands
import sys
import os
import argparse

global lista_salida
global num_lineas

# Manejo de parametros que puede recibir al ejecutar el script
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="Muestra todos los trabajos del usuario <username>")
parser.add_argument("-a", action="store_true", help="Muestra todos los trabajos")



# Obtenemos los parametros que puede recibir el script
args = parser.parse_args()

if(args.username):
	if(args.a):
		# Validamos si el usuario es investigador para poder mostrar la informacion de los trabajos de sus colaboradores y alumnos
		user_id = commands.getoutput("id -u "+args.username)
		if(user_id > 5000 and user_id < 6000):
			info_user = commands.getoutput("cat /etc/passwd | grep "+args.username+" | awk '{ print $1 }'")
			info_user = info_user.split()
			users = []
			for i in info_user:
			    aux = i.split(":")
				users.append(aux[0])
    	else:
			trabajos = commands.getoutput("python jobs.py "+args.username)
			
	else:
		trabajos = commands.getoutput("python jobs.py "+args.username)
    	lista_salida = trabajos.splitlines()
    	num_lineas = len(lista_salida) - 1 
        
    	if(num_lineas == 0):
			sys.stdout.write("\tACTUALMENTE EL USUARIO "+args.username+" NO CUENTA CON TRABAJOS ALOJADOS EN EL SERVIDOR"+"\n")
        	quit()
    	else:
        	num_lineas = str(num_lineas)
	
else: 
    ayuda = commands.getoutput("python slurmwatch.py -h")
    sys.stdout.write("Es necesario especificar el nombre de usuario"+'\n')
    sys.stdout.write('\n'+ayuda+'\n')
    quit()
 
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

def validar_nodo(nodos):
    #Recuperamos el tercer caracter de la cadena para despues validar
    c = nodos[2]
    nodo = ""

    if(c == '['):
	# Si el tercer caracter de la cadena es [ entonces tenemos que
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

def desplegar_ayuda(stdscr):

    k = 0
    stdscr.clear()
    stdscr.refresh()
    
    info_ayuda = {1:"\tq:", 2:"\t\tSalir de la pantalla actual o salir del programa", 3:"\th:", 4: "\t\tMuesta esta pantalla de ayuda"}
    cont_y = 5
    
    while (k != ord('q')):
    
        for i in info_ayuda:
            if(i%2 != 0):
        	stdscr.addstr(cont_y,0, info_ayuda[i], curses.color_pair(6))
		cont_y += 1
            else: 
        	stdscr.addstr(cont_y,0, info_ayuda[i], curses.color_pair(5))
                cont_y += 1 
         
        k = stdscr.getch()

def crear_subpantalla(stdscr, salida):
    k = 0 
    cursor_x = 0
    cursor_y = 1
    
    inicializar_curses(stdscr, cursor_y, cursor_x) 
    
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
    global lista_salida
    k = 0 
    cursor_x = 0
    cursor_y = 1
    inicializar_curses(stdscr, cursor_y, cursor_x) 
    
    #Capturamos cada linea que contiene la variable salida en un arreglo
    height, width = stdscr.getmaxyx()
    nlineasup = 1
    nlineainf = height - 1 
    inilinea = 0
    finlinea = width - 1

    #Diccionario que contiene la informacion de teclas especiales
    info_barra_inf = {1:" q ",2:"Salir",3:" h ", 4: "Ayuda"}
    
    while (k != ord('q')):

        desplegar_pantalla(stdscr, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida, info_barra_inf)
        
        k = stdscr.getch()
        if((k == curses.KEY_DOWN) or (k == curses.KEY_UP) or (k == curses.KEY_LEFT) or (k == curses.KEY_RIGHT) or (k == curses.KEY_NPAGE) or (k == 32) or (k == curses.KEY_PPAGE) or (k == curses.KEY_RESIZE)):
            cursor_y, height, width, nlineasup, nlineainf, inilinea, finlinea= sroll(stdscr, k, cursor_y, cursor_x, height, width, nlineasup, nlineainf, inilinea, finlinea, lista_salida) 
        elif(k == ord('h')):
            desplegar_ayuda(stdscr)
	
 
def main():
    stdscr = curses.initscr()
    height, width = stdscr.getmaxyx()
    if(height >= 20 and width >= 132):
        curses.wrapper(crear_pantalla)
    else:
        if(height < 20 and width < 132):
            terminar()
            sys.stdout.write("TAMANIO DE PANTALLA INSUFICIENTE...........SE REQUIERE UNA PANTALLA MAS AMPLIA"+'\n')
        if(height >= 20 and width < 132):
            terminar()
            sys.stdout.write("TAMANIO DE PANTALLA INSUFICIENTE...........SE REQUIERE UNA PANTALLA CON MAS COLUMNAS"+'\n')
        if(height < 20 and width >= 132):
            terminar()
            sys.stdout.write("TAMANIO DE PANTALLA INSUFICIENTE...........SE REQUIERE UNA PANTALLA CON MAS RENGLONES"+'\n')
if __name__ == "__main__":
    main()


