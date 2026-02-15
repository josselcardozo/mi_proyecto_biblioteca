from flask import Flask, render_template

app = Flask(__name__)

# Página principal
@app.route("/")
def inicio():
    return render_template("index.html")

# Página dinámica de libro
@app.route("/libro/<titulo>")
def libro(titulo):
    return render_template("libro.html", titulo=titulo)

# Página dinámica de usuario
@app.route("/usuario/<nombre>")
def usuario(nombre):
    return render_template("usuario.html", nombre=nombre)


if __name__ == "__main__":
    app.run(debug=True)
