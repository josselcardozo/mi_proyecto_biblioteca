from flask import Flask, render_template, request, redirect
from conexion.conexion import obtener_conexion

app = Flask(__name__)
from inventario.inventario import (
    guardar_txt, leer_txt,
    guardar_json, leer_json,
    guardar_csv, leer_csv
)

from flask import Flask, render_template, request, redirect
from inventario.bd import db
from inventario.productos import Producto

app = Flask(__name__)

# 🔹 Configuración SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 🔹 Crear tablas automáticamente
with app.app_context():
    db.create_all()

# -----------------------------
# INICIO
# -----------------------------
@app.route("/")
def index():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()

    conexion.close()

    return render_template("index.html", libros=libros)

# -----------------------------
# AGREGAR LIBRO
# -----------------------------
@app.route("/agregar", methods=["GET","POST"])
def agregar():

    if request.method == "POST":

        nombre = request.form["nombre"]
        autor = request.form["autor"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = "INSERT INTO libros (nombre, autor, cantidad, precio) VALUES (%s,%s,%s,%s)"
        cursor.execute(sql,(nombre,autor,cantidad,precio))

        conexion.commit()
        conexion.close()

        return redirect("/")

    return render_template("agregar.html")
# -----------------------------
# EDITAR LIBRO
# -----------------------------
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    libro = Producto.query.get_or_404(id)

    if request.method == "POST":
        libro.nombre = request.form["nombre"]
        libro.autor = request.form["autor"]
        libro.cantidad = int(request.form["cantidad"])
        libro.precio = float(request.form["precio"])

        db.session.commit()
        return redirect("/")

    return render_template("editar.html", libro=libro)

# -----------------------------
# ELIMINAR LIBRO
# -----------------------------
@app.route("/eliminar/<int:id>")
def eliminar(id):
    libro = Producto.query.get_or_404(id)

    db.session.delete(libro)
    db.session.commit()

    return redirect("/")


# -----------------------------
# DATOS (TXT, JSON, CSV)
# -----------------------------
@app.route("/datos", methods=["GET", "POST"])
def datos():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]

        guardar_txt(nombre, precio)
        guardar_json(nombre, precio)
        guardar_csv(nombre, precio)

    datos_txt = leer_txt()
    datos_json = leer_json()
    datos_csv = leer_csv()

    return render_template(
        "datos.html",
        datos_txt=datos_txt,
        datos_json=datos_json,
        datos_csv=datos_csv
    )

# -----------------------------
# EJECUTAR
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)