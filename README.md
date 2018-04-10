
## 1. Objetivos de la aplicación.

Mostrar información correspondiente a los trabajos que el usuario tiene alojados en el nodo Yoltla para poder tener una mejor administración de éstos. 

**Modo de impresión**

La información se despliega a través de la terminal en la que se ha sido ejecutada la aplicación.


## 2. Acceso a la aplicación.

La aplicación permite recibir opciones al momento de su ejecución, mismos que se explican a continuación:

|Opción | Función | 
| ------ | ------ |
| -h | Muestra en mensaje de ayuda. |
| -A | Muestra información de trabajos del usuario, colaboradores y alumnos. |
|-tR | Muestra información de trabajos del usuario que se encuentran en ejecución. |
|-tPD | Muestra información de trabajos del usuario que estan pendientes. |
|-l | Muestra información de trabajos del usuario en ejecución y trabajos pendientes. |
|-p | Imprime información acerca de los trabajos en ejecución y trabajos pendientes en la terminal. |

Esta opción sólo esta permitida en modo administrador. 

| Opción | Función |
| ------ | ------ |
| -u USERNAME, --username USERNAME | Permite visualizar la información de los trabajos del usuario <USERNAME> |

Se pueden proporcionar varios nombres de usuario separando a cada uno por "," y sin espacios, ejemplo:

`
user@hostname:~$ slurm-watch -u user1,user2,user3,user4
`

## 3. Opciones durante la ejecución de la aplicación.

La aplicación cuenta con teclas especiales que pueden ser utilizadas durante la ejecución de ésta.  

| Tecla | Función | 
| ------ | ------ |
| q | Salir de la aplicación, o de la ventana en la que se encuentra actualmente. |
| Enter | Ver información acerca del trabajo que actualmente se encuentre seleccionado.|
| u | Muestra información de todos los trabajos en ejecucion y trabajos pendientes del usuario. |
| r | Ver información de los trabajos en ejecución del usuario.|
| p | Permite ver información de los trabajos pendientes del usuario. |
| l | Muestra información de todos los trabajos en ejecucion y trabajos pendientes del usuario. | 
| h	| Despliega una ventana de ayuda. |


Funciones de las teclas especiales en modo administrador.

| Tecla | Función |
| ------- | ------- |
| Enter | Despliega información acerca del trabajo que actualmente se encuentre seleccionado.|
| u | Ver información de todos los trabajos en ejecución y trabajos pendientes del usuario que actualmente se encuentra seleccionado. |
| r | Permite ver información de todos los trabajos que se encuentran en ejecución. |
| p | Muestra información de todos los trabajos pendientes. |
| l | Muestra información de todos los trabajos que se encuentran en ejecución y trabajos pendientes. |

Nota:
Para poder desplazar la información estan como apoyo las teclas barra espaciadora, Re Pág y Av Pág.


<script src="https://asciinema.org/a/7ErMb7TN31zE5I1VdCsTFB1x4.js" id="asciicast-7ErMb7TN31zE5I1VdCsTFB1x4" async></script>

