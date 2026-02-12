from flask import Flask

app = Flask(__name__)

# Ruta principal
@app.route("/")
def inicio():
    return "Bienvenido a Biblioteca Virtual – Sistema desarrollado por Jossel 🚀"


# Ruta dinámica para consultar un libro
@app.route("/libro/<titulo>")
def libro(titulo):
    return f"Libro: {titulo} – consulta realizada correctamente en la Biblioteca Virtual."


# Ruta dinámica para usuario que inicia sesión
@app.route("/usuario/<nombre>")
def usuario(nombre):
    return f"Bienvenido, {nombre}. Tu sesión en la Biblioteca Virtual está activa."


# Ruta dinámica para préstamo de libro
@app.route("/prestamo/<nombre>/<titulo>")
def prestamo(nombre, titulo):
    return f"{nombre}, tu solicitud de préstamo del libro '{titulo}' está en proceso."


if __name__ == "__main__":
    app.run(debug=True)
