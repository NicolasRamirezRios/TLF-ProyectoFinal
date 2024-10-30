import tkinter as tk
from tkinter import messagebox, scrolledtext
import re

# Crear la ventana principal
root = tk.Tk()
root.title("Validador de Expresiones Regulares")
root.geometry("500x600")
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
        for cadena in cadenas:
            if patron.fullmatch(cadena):
                resultado_text.insert(tk.END, f"'{cadena}' - Aceptada ✔️\n", "aceptada")
            else:
                resultado_text.insert(tk.END, f"'{cadena}' - Rechazada ❌\n", "rechazada")

    except re.error as e:
        messagebox.showerror("Error", f"Expresión regular inválida:\n{e}")


# Función para limpiar los campos de texto
def limpiar_campos():
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
