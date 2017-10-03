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
global remoto
# Manejo de parametros que puede recibir al ejecutar el script
parser = argparse.ArgumentParser()
parser.add_argument("-R", action="store_true", help="Permite ejecutar este script de manera remota")
#parser.add_argument("-l", action="store_true", help="Muestra todos los trabajos")
parser.add_argument("-u", "--username", help="Muestra todos los trabajos del usuario <username>")
parser.add_argument("-tR", action="store_true", help="Muestra todos los trabajos en ejecucion")
parser.add_argument("-tPD", action="store_true", help="Muestra todos los trabajos pendientes")

# Obtenemos los parametros que puede recibir el script
args = parser.parse_args()

# Validamos los casos posibles al recibir parametros para indicar que hacer en cada caso
#Validamos que parametros se recibieron para la ejecucion remota del script
if(args.R):
    remoto = True
    if(args.R and args.tR):
        if(args.username):
            salida = commands.getoutput("ssh a.raco squeue -l -tR -u "+args.username)
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
        else: 
            salida = commands.getoutput("ssh a.raco python /LUSTRE/home/uam/izt/pdcs/alumnos/a.raco/squeue/running.py")
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
    elif(args.R and args.tPD):
        if(args.username):
            salida = commands.getoutput("ssh a.raco squeue -l -tPD -u "+args.username)
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
        else:
            salida = commands.getoutput("ssh a.raco squeue -l -tPD")
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
    elif(args.username):
            salida = commands.getoutput("ssh a.raco squeue -l -u "+args.username)
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
    else:
        salida = commands.getoutput("ssh a.raco squeue -l")
        num_lineas = str(len(salida.splitlines())-2)
        lista_salida = salida.splitlines()[1:]
#Validamos las opciones recibidas en la ejecucion del script dentro de un  nodo en el cluster
else:
    remoto = False
    if(args.tR):
        if(args.username):
            salida = commands.getoutput("squeue -l -tR -u "+args.username)
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
        else: 
            salida = commands.getoutput("python /LUSTRE/home/uam/izt/pdcs/alumnos/a.raco/squeue/running.py")
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
    elif(args.tPD):
        if(args.username):
            salida = commands.getoutput("squeue -l -tPD -u "+args.username)
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
        else:
            salida = commands.getoutput("squeue -l -tPD")
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
    elif(args.username):
            salida = commands.getoutput("squeue -l -u "+args.username)
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
    else:
        salida = commands.getoutput("squeue -l")
        num_lineas = str(len(salida.splitlines())-2)
        lista_salida = salida.splitlines()[1:]
    if(len(lista_salida) <= 1):
        ayuda = commands.getoutput("python /LUSTRE/home/uam/izt/pdcs/alumnos/a.raco/squeue/squeue.py -h")
        sys.stdout.write("Es necesario que agregues el parametro \"-R\" para ejecutar el script de manera remota"+'\n')
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
    """
    k = 0
    stdscr.clear()
    stdscr.refresh()
    while (k != ord('q')):
        linea1 = "    Nota: "
        linea2 = "En esta version se implemento el reajuste de la informacion en pantalla"
        linea3 = "en caso de que la terminal sea redimensionada, pero aun no esta perfeccionada"
        linea4 = " q: Salir de la pantalla actual o en caso de estar en la pantalla principal"
        linea5 = "    salir del programa"
        linea6 = " Enter: Muestra informacion acerca del trabajo seleccionado a partir de donde"
        linea7 = "        actualmente esta el cursor, tomando el JOBID"
        linea8 = " w: Hace top al nodo que se ecuentra en la linea seleccionada actualmente"
        linea9 = " e: Se contecta por ssh al nodo y ejecuta pstree con el usuaraio que esta utilizando el nodo"
        linea10 = " h: Muestra esta pantalla de ayuda"
        #stdscr.attron(curses.color_pair(4))
        stdscr.addstr(1, 0, linea1, curses.color_pair(4))
        stdscr.addstr(2, 0, linea2, curses.color_pair(5))
        stdscr.addstr(3, 0, linea3, curses.color_pair(5))
        stdscr.addstr(6,0, linea4[0:3], curses.color_pair(6))
        stdscr.addstr(6,3, linea4[3:], curses.color_pair(5))
        stdscr.addstr(7,0, linea5, curses.color_pair(5))
        stdscr.addstr(9,0, linea6[0:7], curses.color_pair(6))
        stdscr.addstr(9,7, linea6[7:], curses.color_pair(5))
        stdscr.addstr(10,0, linea7, curses.color_pair(5))
        stdscr.addstr(12,0, linea8[0:3], curses.color_pair(6))
        stdscr.addstr(12,3, linea8[3:], curses.color_pair(5))
        stdscr.addstr(14,0, linea9[0:3], curses.color_pair(6))
        stdscr.addstr(14,3, linea9[3:], curses.color_pair(5))
        stdscr.addstr(16,0, linea10[0:3], curses.color_pair(6))
        stdscr.addstr(16,3, linea10[3:], curses.color_pair(5))
        #stdscr.attroff(curses.color_pair(4))
         
        k = stdscr.getch()
    """
    k = 0
    stdscr.clear()
    stdscr.refresh()
    
    while(k != ord('q')):
        os.system("less Ayuda.md")
        k = 113
    curses.endwin()

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
            #Recuperamos la informacion de la linea en la que actualmente estael cursor
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            #Guardamos cada una de las cadenas que contiene la linea en un arreglo
            datos = linea.split()
	    jobid = datos[-9]
    	    salida =  commands.getoutput("scontrol show jobid -dd  "+jobid)
            crear_subpantalla(stdscr, salida)
        elif(k == ord('w')):
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos = linea.split()
	    nodo = validar_nodo(datos[-1])
	    crear_pantalla_htop(stdscr, nodo)
        elif(k == ord('e')):
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos =  linea.split()
	    usr = datos[-6]
	    nodo = datos[-1]
	    salida = commands.getoutput("ssh "+nodo+" pstree -u "+usr+" -plac")
            crear_subpantalla(stdscr, salida)
        elif(k == ord('u')):
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos = linea.split()
            usuario = datos[-6]
            if(remoto == True):
	        salida = commands.getoutput("ssh a.raco squeue -l -u "+usuario)
            else:
	        salida = commands.getoutput("squeue -l -u  "+usuario)
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
            cursor_x = 0
            cursor_y = 1
    	    height, width = stdscr.getmaxyx()
    	    nlineasup = 1
    	    nlineainf = height - 1 
    	    inilinea = 0
    	    finlinea = width - 1
        elif(k == ord('t')):
            salida = commands.getoutput("less /LUSTRE/home/uam/izt/pdcs/RAUL/sq.py")
            crear_subpantalla(stdscr, salida)
        elif(k == ord('r')):
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos = linea.split()
            usuario = datos[-6]
            if(remoto == True):
	        salida = commands.getoutput("ssh a.raco python /LUSTRE/home/uam/izt/pdcs/alumnos/a.raco/squeue/running.py "+usuario)
            else:
	        salida = commands.getoutput("python /LUSTRE/home/uam/izt/pdcs/alumnos/a.raco/squeue/running.py "+usuario)
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
	        salida = commands.getoutput("ssh a.raco python /LUSTRE/home/uam/izt/pdcs/alumnos/a.raco/squeue/running.py")
            else:
	        salida = commands.getoutput("python /LUSTRE/home/uam/izt/pdcs/alumnos/a.raco/squeue/running.py")
            num_lineas = str(len(salida.splitlines())-1)
            lista_salida = salida.splitlines()
            cursor_x = 0
            cursor_y = 1
	elif(k == ord('p')):
            linea = recuperar_linea(lista_salida, cursor_y, nlineasup, nlineainf)
            datos = linea.split()
            usuario = datos[-6]
            if(remoto == True):
	        salida = commands.getoutput("ssh a.raco squeue -l -tPD -u "+usuario)
            else:
	        salida = commands.getoutput("squeue -l -tPD -u "+usuario)
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
            cursor_x = 0
            cursor_y = 1
    	    height, width = stdscr.getmaxyx()
    	    nlineasup = 1
    	    nlineainf = height - 1 
    	    inilinea = 0
    	    finlinea = width - 1
        elif(k == ord('P')):
            if(remoto == True):
	        salida = commands.getoutput("ssh a.raco squeue -l -tPD ")
            else:
	        salida = commands.getoutput("squeue -l -tPD ")
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
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
            if(remoto == True):
	        salida = commands.getoutput("ssh a.raco squeue -l")
            else:
	        salida = commands.getoutput("squeue -l ")
            num_lineas = str(len(salida.splitlines())-2)
            lista_salida = salida.splitlines()[1:]
            cursor_x = 0
            cursor_y = 1
    	    # Esto porque como es consulta probablemente el resultado sera de menos lineas por lo que vamos a reestablecer las variables
	    # a sus valores de inicio para que no halla problema al momento de mostrar la informacion en pantalla 
	    height, width = stdscr.getmaxyx()
    	    nlineasup = 1
    	    nlineainf = height - 1 
    	    inilinea = 0
    	    finlinea = width - 1
	elif(k == ord('h')):
            desplegar_ayuda(stdscr)
        
	
 
def main():
    stdscr = curses.initscr()
    height, width = stdscr.getmaxyx()
    if(height >= 20 and width >= 117):
        curses.wrapper(crear_pantalla)
    else:
        if(height < 20 and width < 117):
            terminar()
            sys.stdout.write("TAMANIO DE PANTALLA INSUFICIENTE...........SE REQUIERE UNA PANTALLA MAS AMPLIA"+'\n')
        if(height >= 20 and width < 117):
            terminar()
            sys.stdout.write("TAMANIO DE PANTALLA INSUFICIENTE...........SE REQUIERE UNA PANTALLA CON MAS COLUMNAS"+'\n')
        if(height < 20 and width >= 117):
            terminar()
            sys.stdout.write("TAMANIO DE PANTALLA INSUFICIENTE...........SE REQUIERE UNA PANTALLA CON MAS RENGLONES"+'\n')
if __name__ == "__main__":
    main()


