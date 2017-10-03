# MANUAL DE USUARIO


## 1. OBJETIVOS DE LA APLICACION

Permitir la impresión de la información correspondiente a los trabajos que estan alojados en el servidor para poder tener una mejor administración de éstos. 

**Modo de impresión**

La aplicación permite desplegar a través de una terminal la información obtenida de los trabajos alojados en el servidor.


## 2. INGRESO A LA APLICACION

La aplicación contempla el uso de parámetros al momento de su ejecución, los parámetros que acepta y la explicación de la información que éstos muestran se describe a continuación: 

-R  
    Permite ejecutar la aplicación y consultar la información de forma remota en el servidor.  

-u USERNAME, --username USERNAME  
    Muestra la información de todos los trabajos del usuario <USERNAME>  

-tR  
 	Muestra la información de los trabajos que se encuentran en ejecución.  

-tPD  
	Muestra la información de los trabajos pendientes.  

-h  
	Muestra una breve ayuda sobre los parametros que acepta la aplicacion.  


En caso de que no se utilicen parametros al ejecutar la aplicación se mostrará la información de todos los trabajos alojados en el servidor.  

## 3. OPCIONES DURANTE LA EJECUCION DE LA APLICACION

La aplicación cuenta con teclas especiales que pueden ser utilizadas durante la ejecución de ésta.  
q:  
	Salir de la aplicación, o de la ventana en la que se encuentra actualmente.  
Enter:  
	Permite visualizar información acerca del trabajo que se encuentra seleccionado.  
w:  
	Permite hacer una conexión por ssh al nodo que actualmente se encuentra seleccionado y hacer top.  
e:  
	Permite hacer una conexión por ssh al nodo que actualmente se encuentra seleccionado y hacer pstree usando como parámetro el usuario.  
u:  
	Muestra la información de todos los trabajos del usuario que actualmente esta seleccionado.  
p:  
	Muestra la información de todos los trabajos pendientes del usuario que actualmente esta seleccionado.  
r:  
	Muestra la información de todos los trabajos en enjecución del usuario que actualmente esta seleccionado.  
R:  
	Despliega la información de todos los trabajos que estan en ejecución.  
P:  
	Despliega la información de todos los trabajos pendientes.  
l:  
	Muesta la información de todos los trabajos.  
h:  
	Despliega una pequeña ayuda explicando el funcionamiento de las teclas especiales.  



