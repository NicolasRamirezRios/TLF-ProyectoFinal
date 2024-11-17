import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
from PIL import Image, ImageTk
import os
import graphviz
from tkinter import messagebox
import tempfile
import shutil

# Crear la ventana principal
root = tk.Tk()
root.title("Validador y Generador de AFND")
root.geometry("500x700")
root.config(bg="#2E2E2E")

# Función para realizar la validación
def validar_regex():
    resultado_text.delete(1.0, tk.END)  # Limpiar área de resultados
    try:
        # Obtener la expresión regular ingresada
        regex = regex_entry.get()
        if not regex:
            messagebox.showwarning("Advertencia", "Por favor ingresa una expresión regular.")
            return

        # Compilar la expresión regular
        patron = re.compile(regex)

        # Obtener las cadenas a validar
        cadenas = cadenas_text.get(1.0, tk.END).strip().splitlines()
        if not cadenas:
            messagebox.showwarning("Advertencia", "Por favor ingresa al menos una cadena para validar.")
            return

        # Validar cada cadena y mostrar resultados
        global cadenas_validas
        cadenas_validas = []
        for cadena in cadenas:
            if patron.fullmatch(cadena):
                resultado_text.insert(tk.END, f"'{cadena}' - Aceptada ✔️\n", "aceptada")
                cadenas_validas.append(cadena)
            else:
                resultado_text.insert(tk.END, f"'{cadena}' - Rechazada ❌\n", "rechazada")

    except re.error as e:
        messagebox.showerror("Error", f"Expresión regular inválida:\n{e}")


ventana_grafico = None

def cerrar_ventana_grafico():
    global ventana_grafico
    if ventana_grafico is not None and ventana_grafico.winfo_exists():
        ventana_grafico.destroy()
        ventana_grafico = None



def graficar_afnd():
    global ventana_grafico
    if not cadenas_validas:
        messagebox.showwarning("Advertencia", "No hay cadenas válidas para graficar.")
        return

    # Cerrar cualquier ventana de gráfico existente
    cerrar_ventana_grafico()

    # Crear un autómata en formato DOT
    automata = graphviz.Digraph(format='png')
    automata.attr(rankdir='LR')
    automata.attr('node', shape='circle')

    # Estado inicial
    automata.node('q0', label='q0', shape='circle')

    nodos_creados = {'q0'}  # Evitar repetición de nodos
    transiciones = []       # Lista de transiciones
    estados_finales = set() # Estados finales donde terminan las cadenas válidas

    # Crear un diccionario para manejar los estados comunes
    estado_comun = {}

    # Contador para numerar los estados de forma simple
    contador_estado = 1

    # Generar nodos y transiciones para las cadenas válidas
    for cadena in cadenas_validas:
        estado_actual = 'q0'
        for simbolo in cadena:
            if (estado_actual, simbolo) not in estado_comun:
                estado_siguiente = f'q{contador_estado}'  # Usar un número simple para el nodo
                contador_estado += 1  # Incrementar el contador para el siguiente nodo
                estado_comun[(estado_actual, simbolo)] = estado_siguiente  # Mapear transiciones
                # Crear el nodo si no existe
                if estado_siguiente not in nodos_creados:
                    nodos_creados.add(estado_siguiente)
                    automata.node(estado_siguiente, shape='circle')
                # Agregar la transición
                transiciones.append((estado_actual, simbolo, estado_siguiente))
                automata.edge(estado_actual, estado_siguiente, label=simbolo)
            else:
                estado_siguiente = estado_comun[(estado_actual, simbolo)]  # Obtener el nodo común

            estado_actual = estado_siguiente

        # Marcar el estado final para esta cadena
        estados_finales.add(estado_actual)

    # Cambiar los estados finales a doble círculo
    for estado_final in estados_finales:
        automata.node(estado_final, shape='doublecircle')

    # Generar una ruta temporal para el archivo .png
    temp_dir = tempfile.mkdtemp()  # Directorio temporal
    output_file = os.path.join(temp_dir, 'afnd')  # Archivo de salida sin extensión

    # Renderizar el gráfico y asegurarse de que el formato sea PNG
    automata.render(output_file, cleanup=True)

    # Verificar que el archivo .png ha sido generado
    png_file = output_file + '.png'
    if not os.path.exists(png_file):
        messagebox.showerror("Error", "No se pudo generar el archivo PNG.")
        return

    # Mostrar el gráfico en una ventana (asumiendo que la función 'mostrar_grafico' se ajusta para abrir el archivo PNG)
    mostrar_grafico(png_file)

    # Limpiar el directorio temporal después de mostrar el gráfico
    shutil.rmtree(temp_dir)




def mostrar_grafico(ruta):
    global ventana_grafico
    ventana_grafico = tk.Toplevel(root)
    ventana_grafico.title("AFND Generado")

    img = Image.open(ruta)
    img.thumbnail((600, 400))
    img = ImageTk.PhotoImage(img)

    label_imagen = tk.Label(ventana_grafico, image=img)
    label_imagen.image = img
    label_imagen.pack()

def limpiar_campos():
    # Cerrar la ventana del gráfico, si existe
    cerrar_ventana_grafico()

    # Limpiar campos de texto
    regex_entry.delete(0, tk.END)  # Limpiar entrada de expresión regular
    cadenas_text.delete(1.0, tk.END)  # Limpiar área de cadenas
    resultado_text.delete(1.0, tk.END)  # Limpiar área de resultados


# Configurar estilos de texto
def configurar_estilos():
    resultado_text.tag_configure("aceptada", foreground="green")
    resultado_text.tag_configure("rechazada", foreground="red")


# Crear y organizar los widgets
tk.Label(root, text="Expresión Regular:", bg="#2E2E2E", fg="#B0B0B0").pack(pady=(10, 5))  # Gris claro
regex_entry = tk.Entry(root, font=("Helvetica", 14), fg="#FFFFFF", bg="#3E3E3E")  # Texto blanco en entrada
regex_entry.pack(pady=5, padx=10, fill=tk.X)

tk.Label(root, text="Cadenas a validar (una por línea):", bg="#2E2E2E", fg="#B0B0B0").pack(pady=(10, 5))  # Gris claro
cadenas_text = scrolledtext.ScrolledText(root, font=("Helvetica", 12), height=10, fg="#FFFFFF",
                                         bg="#3E3E3E")  # Texto blanco
cadenas_text.pack(pady=5, padx=10, fill=tk.BOTH)

validar_btn = tk.Button(root, text="Validar", command=validar_regex, bg="#28A745", fg="#FFFFFF",
                        font=("Helvetica", 14))  # Verde claro
validar_btn.pack(pady=15)

graficar_btn = tk.Button(root, text="Graficar AFND", command=graficar_afnd, bg="#F0AD4E", fg="#FFFFFF",
                         font=("Helvetica", 14))  # Amarillo
graficar_btn.pack(pady=5)

limpiar_btn = tk.Button(root, text="Limpiar", command=limpiar_campos, bg="#357EDD", fg="#FFFFFF",
                        font=("Helvetica", 14))  # Azul suave
limpiar_btn.pack(pady=5)

tk.Label(root, text="Resultados:", bg="#2E2E2E", fg="#B0B0B0").pack(pady=(10, 5))  # Gris claro
resultado_text = scrolledtext.ScrolledText(root, font=("Helvetica", 12), height=10, fg="#FFFFFF",
                                           bg="#3E3E3E")  # Texto blanco
resultado_text.pack(pady=5, padx=10, fill=tk.BOTH)

configurar_estilos()

# Iniciar el loop de la aplicación
root.mainloop()
