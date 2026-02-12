from flask import Flask
import os

app = Flask(__name__)

# Ruta principal
@app.route('/')
def inicio():
    return "Bienvenido a Biblioteca Virtual – Sistema desarrollado por Jossel 🚀"

# Ruta dinámica para libros
@app.route('/libro/<titulo>')
def libro(titulo):
    return f"Libro: {titulo} – consulta exitosa en el sistema de Jossel."

# Ruta dinámica para usuario
@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f"Bienvenido, {nombre}. Tu sesión en la Biblioteca está activa. – Proyecto de Jossel"


# SOLO para ejecución local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

