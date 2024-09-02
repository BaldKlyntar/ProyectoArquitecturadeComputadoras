import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import serial
import time
import os
from CTkMessagebox import CTkMessagebox
import threading
import datetime
from tkfontawesome import icon_to_image


# Se agregan la paqueteria de serial y customtkinter
# serial se utilizara para controlar el arduino y customtkinter para crear
# la interfaz grafica

arduino = serial.Serial()
root = ctk.CTk()
puerto_seleccionado = ctk.StringVar(root)

# Funcion para configurar el tamaño y posicion de la ventana
# de la interfaz
def screenSize():
    
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    x_pos = int(width / 2 - 770 / 2)
    y_pos = int(height / 2 - 550 / 2)
    root.geometry(f"770x550+{x_pos}+{y_pos}")
    root.resizable(False, False)

# funcion activar que abrira el puerto asignador
# de la placa arduino y enviara el byte R para
# verificar y iniciar la comunicacion

def activar():

    try:

        arduino.port = puerto_seleccionado.get()
        arduino.baudrate = 9600
        arduino.open()

        arduino.write(b'R')
        Verificacion()
        

# Para las excepciones se utilizara CTKMessagebox la cual
# es una ventana emergente que informa al usuario del problema
# que se esta presentando
    except:

        CTkMessagebox(

            title = "Warning",
            message= "Puerto no disponible",
            icon= "warning"
            )

# La funcion desactivar se aloja en el boton del mismo nombre de
# la interfaz la cual despues de ingresar correctamente la 
# contraseña desactiva la alarma  
def desactivar():

    message_desactivar = ctk.CTkInputDialog(

    text= "Ingrese la contraseña",
    font = ("Unispace", 12),
    title = "Verificacion",
    )

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    x_pos = int(width / 2 - 250 / 2)
    y_pos = int(height / 2 - 200 / 2)
    message_desactivar.geometry(f"250x200+{x_pos}+{y_pos}")

    apagado_bytes = message_desactivar.get_input()
    if apagado_bytes == "1234":

        arduino.write(apagado_bytes.encode('utf-8'))
        
        btn_reiniciar.configure(state = tk.ACTIVE)
        btn_desactivar.configure(state = tk.DISABLED)
        btn_salir.configure(state= tk.ACTIVE)
        root.protocol("WM_DELETE_WINDOW", abierto)  

    elif apagado_bytes == None:

        pass

    else:
        
        CTkMessagebox(

        title = "Warning",
        message= "Contraseña Incorrecta",
        icon= "warning"
        )

# la funcion reiniciar cierra el puerto de arduino
# y borra las lecturas de la fotorresistencia  
def reiniciar():

    arduino.close()
    status_textbox.delete('1.0', tk.END)
    btn_activar.configure(state = tk.ACTIVE)
    


# La funcion verificacion se llama dentro de la
# funcion activar donde despues de abrir el puerto
# y verificar que se tiene comunicacion con la placa
# pregunta al usuario por la contraseña para activarla


        
def Verificacion():

    message_activar = ctk.CTkInputDialog(

    text= "Ingrese la contraseña",
    font = ("Unispace", 12),
    title = "Verificacion",
    )

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    x_pos = int(width / 2 - 250 / 2)
    y_pos = int(height / 2 - 200 / 2)
    message_activar.geometry(f"250x200+{x_pos}+{y_pos}")
    message_activar.configure(show ="*")

    contraseña_bytes = message_activar.get_input()
    if contraseña_bytes == "1234":

        arduino.write(contraseña_bytes.encode('utf-8'))
        btn_activar.configure(state = tk.DISABLED)
        btn_reiniciar.configure(state = tk.DISABLED)
        
        Alarma()

    elif contraseña_bytes == None:
       
       reiniciar()
       pass
        
    else:
        
        CTkMessagebox(

        title = "Warning",
        message= "Contraseña Incorrecta",
        icon= "warning"
        )

        reiniciar()




# Despues de la funcion verificacion finalmente
# se llama a la funcion alarma la cual realiza una llamada
# recursiva con la funcion proceso para imprimir los valores recibidos
# por la fotorresistencia, se utiliza after para realizar el
# proceso cada cierto tiempo evitando que se causen problemas con
# el ciclo principal de la aplicacion (mainloop)

def Alarma():
    # protocolo para bloquear el boton "x" de salida en conjunto con la
    # funcion cerrado
    root.protocol("WM_DELETE_WINDOW", cerrado)  
    btn_salir.configure(state= tk.DISABLED)
    btn_desactivar.configure(state= tk.ACTIVE)
    respuesta = arduino.readline().decode('utf-8').strip()

    if respuesta == 'Alarma activada!':

        root.after(100, Proceso)
        
    else:

        CTkMessagebox(

        title = "Error",
        message= "Alarma no disponible",
        icon= "warning"
        )

def Proceso():

    # Se crean las variables hora actual y estado_luz, hora actual
    # hace uso de datetime para recibir la hora a tiempo real
    # estado_luz recibe los valores de la fotorresistencia
    hora_actual = str(datetime.datetime.now().strftime("%H:%M"))
    estado_luz = arduino.readline().decode('utf-8').strip()
    status_textbox.insert(
        
        tk.END, 'STATUS: ' + estado_luz + '  ' + hora_actual + '\r\n'
        
    )
    root.update_idletasks()
    
    try:


        if int(estado_luz) > 500:

            CTkMessagebox(

            title = "Advertencia",
            message= "Movimiento detectado",
            icon= "info"
            )
            

        else:

            root.after(300, Proceso)

    except:

        CTkMessagebox(

        title = "Advertencia",
        message= "Alarma Desactivada",
        icon= "info"
        )

# Funcion para cerrar la ventana        
def cerrar_ventana():
    root.destroy()

# Funcion para inhabilitar el boton "x" de la salida de la aplicacion
def cerrado():

    return
# Funcion para habilitar el boton "x" despues de desactivar la alarma
def abierto():

    cerrar_ventana()

    
# Creacion de la interfaz grafica aqui se crea el diseño
# de los botones, label y demas atributos

# Se llama a la funcion ScreenSize para ajustar la ventana de
# la aplicacion
screenSize()
# Se establece el titulo de la pestaña de la aplicacion
# y los labels
root.title("Control de Alarma")

lbl_header = ctk.CTkLabel(root, text= "Control de Alarma",
                                font = ("Unispace", 20))
lbl_puerto = ctk.CTkLabel(root, text= "Puerto",
                                font = ("Unispace", 14))

# Creacion de el combo box que aloja las opciones del
# puerto de arduino
combo_puerto = ctk.CTkComboBox(

    root,
    values = ["COM1", "COM2", "COM3", 'COM4'],
    variable=puerto_seleccionado
)

lbl_status = ctk.CTkLabel(root, text= "Estado de la alarma",
                                font = ("Unispace", 14), fg_color= '#1F6AA5')

# Textbox que imprime los valores de la fotorresistencia
status_textbox = ctk.CTkTextbox(

    root,
    width = 370,
    height = 490,
    corner_radius = 100,
    font = ("Unispace", 14),
    border_spacing= 0,
    border_width= 20,
    border_color= '#1F6AA5'
    
)


# Creacion del boton activar
btn_activar = ctk.CTkButton(

    root,
    text = "Activar",
    font = ("Unispace", 12),
    width = 140,
    command = activar 
)

# Creacion del boton desactivar
btn_desactivar = ctk.CTkButton(

    root,
    text = "Desactivar",
    font = ("Unispace", 12),
    width = 140,
    command = desactivar
)

# Creacion del boton reiniciar
btn_reiniciar = ctk.CTkButton(

    root,
    text = "Reiniciar",
    font = ("Unispace", 12),
    width = 140,
    command = reiniciar
)

# Creacion del boton salir

btn_salir = ctk.CTkButton(

    root,
    text = "Salir",
    font = ("Unispace", 12),
    width = 140,
    command = cerrar_ventana
)

# Creacion del logotipo (imagen del dragon en la esquina superior izquierda)
send = icon_to_image("dragon", fill="#1F6AA5", scale_to_width=80)
ctk.CTkLabel(root, image=send, text = "").place(x = 20, y = 20)

# Posicionamiento de los widgets (imagenes, labels, botones, etc)
lbl_puerto.place(x = 20, y = 110 )
status_textbox.place(x = 380, y = 30)
btn_activar.place(x = 20, y = 350)
btn_desactivar.place(x = 20, y = 400)
btn_reiniciar.place(x = 20, y = 450)
btn_salir.place(x = 20, y = 500)
combo_puerto.place(x = 20, y = 150)
# El boton desactivar inicia inhabilitado para evitar errores
btn_desactivar.configure(state = tk.DISABLED)




root.mainloop()

            

            




       

        

