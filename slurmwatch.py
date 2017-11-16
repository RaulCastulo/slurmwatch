#!/usr/bin/env python
import curses
import commands
import sys
import os
import argparse

# Variables en donde se guardara la informacion que se obtiene de ejecutar los comandos
global salida  
global num_lineas
global lista_salida

def validar_usuario_investigador(usuario):
	usuarios = " "
	id_inferior = 5000
	id_superior = 6000
	#sys.stdout.write(usuario+"\n")
	user_id = int(commands.getoutput("id -u "+usuario))
	#user_id = int(commands.getoutput("echo $UID ")
	#sys.stdout.write(str(user_id)+"\n")
	if((id_inferior < user_id) and (user_id < id_superior)):
		info_user = commands.getoutput("cat /etc/passwd | grep "+usuario+" | awk '{ print $1 }'")
		info_user = info_user.split()
		users = []
		for i in info_user:
			aux = i.split(":")
			users.append(aux[0])
		usuarios = " ".join(users)
		#sys.stdout.write(usuarios+"\n")
	else:
		usuarios = usuario
	return usuarios

# Manejo de parametros que puede recibir al ejecutar el script
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="Muestra todos los trabajos del usuario <username>")
parser.add_argument("-A", action="store_true", help="Muestra todos los trabajos")
parser.add_argument("-p", action="store_true", help="Imprime la informacion en la terminal")

# Obtenemos los parametros que puede recibir el script
args = parser.parse_args()

# Validamos los casos posibles al recibir parametros para indicar que hacer en cada caso

if(args.username):
	if(args.A):
		usuarios = validar_usuario_investigador(args.username)
		if(args.p):
			trabajos = commands.getoutput("python jobs.py "+usuarios+" | awk '{print $1,$2,$3,$4,$5,$6,$10}' | column -t ")
			sys.stdout.write(trabajos+"\n")
			quit()
		else:
			trabajos = commands.getoutput("python jobs.py "+usuarios)
			lista_salida = trabajos.splitlines()
			num_lineas = str(len(lista_salida) - 1)
	elif(args.p):
		trabajos = commands.getoutput("python jobs.py "+args.username+" | awk '{print $1,$2,$3,$4,$5,$6,$10}' | column -t ")
		sys.stdout.write(trabajos+"\n")
		quit()
	else:
		trabajos = commands.getoutput("python jobs.py "+args.username)
		lista_salida = trabajos.splitlines()
		num_lineas = str(len(lista_salida) - 1)
else:
	usuario = commands.getoutput("echo $USER")
	trabajos = commands.getoutput("python jobs.py "+usuario)
	lista_salida = trabajos.splitlines()
	num_lineas = str(len(lista_salida) - 1)

if(len(lista_salida) == 1):
	sys.stdout.write("No cuentas con trabajos alojados en el servidor\n")
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
	"""
	
	"""
	try:
		main()
	except KeyboardInterrupt:
		terminar()

