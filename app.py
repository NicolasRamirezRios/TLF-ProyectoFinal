import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
import os
import graphviz
import tempfile
import shutil

# Crear la ventana principal de la aplicación
root = tk.Tk()
root.title("Validador y Generador de AFND")
root.geometry("500x700")
root.config(bg="#2E2E2E")

# Variables globales
ventana_grafico = None  # Referencia a la ventana que muestra el gráfico
cadenas_validas = []    # Lista de cadenas que cumplen con la expresión regular


def validar_regex():
    """
    Valida las cadenas ingresadas contra una expresión regular proporcionada por el usuario.
    Actualiza la interfaz para mostrar los resultados.
    """
    resultado_text.delete(1.0, tk.END)  # Limpiar área de resultados

    try:
        # Obtener la expresión regular ingresada
        regex = regex_entry.get()
        if not regex:
            messagebox.showwarning("Advertencia", "Por favor ingresa una expresión regular.")
            return

        # Compilar la expresión regular
        patron = re.compile(regex)

        # Obtener las cadenas ingresadas por el usuario
        cadenas = cadenas_text.get(1.0, tk.END).strip().splitlines()
        if not cadenas:
            messagebox.showwarning("Advertencia", "Por favor ingresa al menos una cadena para validar.")
            return

        # Validar cada cadena y almacenar las válidas
        global cadenas_validas
        cadenas_validas = []
        for cadena in cadenas:
            if patron.fullmatch(cadena):
                resultado_text.insert(tk.END, f"'{cadena}' - Aceptada ✔️\n", "aceptada")
                cadenas_validas.append(cadena)
            else:
                resultado_text.insert(tk.END, f"'{cadena}' - Rechazada ❌\n", "rechazada")

    except re.error as e:
        # Mostrar un mensaje de error si la expresión regular no es válida
        messagebox.showerror("Error", f"Expresión regular inválida:\n{e}")


def graficar_afnd():
    """
    Genera un autómata finito no determinista (AFND) a partir de las cadenas válidas.
    Muestra el gráfico resultante en una nueva ventana.
    Guarda el gráfico en una carpeta llamada 'AFND' en el mismo directorio donde está el código.
    """
    global ventana_grafico

    if not cadenas_validas:
        messagebox.showwarning("Advertencia", "No hay cadenas válidas para graficar.")
        return

    # Cerrar cualquier ventana de gráfico existente
    cerrar_ventana_grafico()

    # Crear el grafo del autómata utilizando Graphviz
    automata = graphviz.Digraph(format='png')
    automata.attr(rankdir='LR')  # Direccionar el grafo de izquierda a derecha
    automata.attr('node', shape='circle')

    # Definir el estado inicial
    automata.node('q0', label='q0', shape='circle')

    nodos_creados = {'q0'}        # Conjunto para evitar duplicación de nodos
    transiciones = []            # Lista de transiciones agregadas
    estados_finales = set()      # Conjunto de estados finales
    estado_comun = {}            # Diccionario para estados compartidos
    contador_estado = 1          # Contador para nombrar los nodos

    # Crear nodos y transiciones para cada cadena válida
    for cadena in cadenas_validas:
        estado_actual = 'q0'  # Siempre comenzamos desde el estado inicial
        for simbolo in cadena:
            # Crear una nueva transición si no existe
            if (estado_actual, simbolo) not in estado_comun:
                estado_siguiente = f'q{contador_estado}'
                contador_estado += 1
                estado_comun[(estado_actual, simbolo)] = estado_siguiente
                # Crear nodo si no ha sido creado
                if estado_siguiente not in nodos_creados:
                    nodos_creados.add(estado_siguiente)
                    automata.node(estado_siguiente, shape='circle')
                # Agregar transición al grafo
                transiciones.append((estado_actual, simbolo, estado_siguiente))
                automata.edge(estado_actual, estado_siguiente, label=simbolo)
            else:
                estado_siguiente = estado_comun[(estado_actual, simbolo)]

            estado_actual = estado_siguiente

        # Marcar el estado final
        estados_finales.add(estado_actual)

    # Marcar estados finales con doble círculo
    for estado_final in estados_finales:
        automata.node(estado_final, shape='doublecircle')

    # Obtener el directorio actual donde se encuentra el código
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Crear la carpeta 'AFND' si no existe
    output_dir = os.path.join(current_dir, 'AFND')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Ruta completa para guardar la imagen
    output_file = os.path.join(output_dir, 'afnd')

    # Guardar el gráfico en un archivo en el directorio 'AFND'
    automata.render(output_file, cleanup=True)

    # Ruta del archivo PNG generado
    png_file = output_file + '.png'
    if os.path.exists(png_file):
        mostrar_grafico(png_file)  # Función para mostrar el gráfico, si es necesario
    else:
        messagebox.showerror("Error", "No se pudo generar el archivo PNG.")


def mostrar_grafico(ruta):
    """
    Abre una nueva ventana para mostrar el gráfico generado.
    """
    global ventana_grafico
    ventana_grafico = tk.Toplevel(root)
    ventana_grafico.title("AFND Generado")

    # Usar tkinter.PhotoImage para cargar la imagen PNG
    img = tk.PhotoImage(file=ruta)

    # Mostrar la imagen en un widget Label
    label_imagen = tk.Label(ventana_grafico, image=img)
    label_imagen.image = img  # Referencia para evitar recolección de basura
    label_imagen.pack()

def cerrar_ventana_grafico():
    """
    Cierra la ventana de gráfico si está abierta.
    """
    global ventana_grafico
    if ventana_grafico is not None and ventana_grafico.winfo_exists():
        ventana_grafico.destroy()
        ventana_grafico = None

def limpiar_campos():
    """
    Limpia los campos de texto y cierra la ventana de gráfico si está abierta.
    """
    cerrar_ventana_grafico()  # Cerrar la ventana del gráfico
    regex_entry.delete(0, tk.END)  # Limpiar la entrada de expresión regular
    cadenas_text.delete(1.0, tk.END)  # Limpiar el área de texto para las cadenas
    resultado_text.delete(1.0, tk.END)  # Limpiar el área de resultados


def configurar_estilos():
    """
    Configura los estilos de texto para el área de resultados.
    """
    resultado_text.tag_configure("aceptada", foreground="green")
    resultado_text.tag_configure("rechazada", foreground="red")


# Configuración de la interfaz gráfica
tk.Label(root, text="Expresión Regular:", bg="#2E2E2E", fg="#B0B0B0").pack(pady=(10, 5))
regex_entry = tk.Entry(root, font=("Helvetica", 14), fg="#FFFFFF", bg="#3E3E3E")
regex_entry.pack(pady=5, padx=10, fill=tk.X)

tk.Label(root, text="Cadenas a validar (una por línea):", bg="#2E2E2E", fg="#B0B0B0").pack(pady=(10, 5))
cadenas_text = scrolledtext.ScrolledText(root, font=("Helvetica", 12), height=10, fg="#FFFFFF", bg="#3E3E3E")
cadenas_text.pack(pady=5, padx=10, fill=tk.BOTH)

validar_btn = tk.Button(root, text="Validar", command=validar_regex, bg="#28A745", fg="#FFFFFF", font=("Helvetica", 14))
validar_btn.pack(pady=15)

graficar_btn = tk.Button(root, text="Graficar AFND", command=graficar_afnd, bg="#F0AD4E", fg="#FFFFFF", font=("Helvetica", 14))
graficar_btn.pack(pady=5)

limpiar_btn = tk.Button(root, text="Limpiar", command=limpiar_campos, bg="#357EDD", fg="#FFFFFF", font=("Helvetica", 14))
limpiar_btn.pack(pady=5)

tk.Label(root, text="Resultados:", bg="#2E2E2E", fg="#B0B0B0").pack(pady=(10, 5))
resultado_text = scrolledtext.ScrolledText(root, font=("Helvetica", 12), height=10, fg="#FFFFFF", bg="#3E3E3E")
resultado_text.pack(pady=5, padx=10, fill=tk.BOTH)

configurar_estilos()

# Iniciar el bucle principal de la aplicación
root.mainloop()
