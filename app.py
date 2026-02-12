from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return "Bienvenido a Biblioteca Virtual – Consulta de libros disponibles"

@app.route('/libro/<titulo>')
def libro(titulo):
    return f"Libro: {titulo} – consulta exitosa."

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f"Bienvenido, {nombre}. Tu sesión en la Biblioteca está activa."

print(">>> Aplicación Flask iniciando...")

app.run(host="127.0.0.1", port=5000, debug=True)
