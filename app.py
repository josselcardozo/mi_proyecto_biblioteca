from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# -----------------------------
# CREAR TABLA
# -----------------------------
def crear_tabla():
    conexion = sqlite3.connect("biblioteca.db")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            autor TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


# -----------------------------
# OBTENER LIBROS
# -----------------------------
def obtener_libros():
    conexion = sqlite3.connect("biblioteca.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()

    conexion.close()
    return libros


# -----------------------------
# AGREGAR LIBRO
# -----------------------------
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        autor = request.form["autor"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        conexion = sqlite3.connect("biblioteca.db")
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO libros (nombre, autor, cantidad, precio)
            VALUES (?, ?, ?, ?)
        """, (nombre, autor, cantidad, precio))

        conexion.commit()
        conexion.close()

        return redirect("/")

    return render_template("agregar.html")


# -----------------------------
# EDITAR LIBRO
# -----------------------------
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexion = sqlite3.connect("biblioteca.db")
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        autor = request.form["autor"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        cursor.execute("""
            UPDATE libros
            SET nombre = ?, autor = ?, cantidad = ?, precio = ?
            WHERE id = ?
        """, (nombre, autor, cantidad, precio, id))

        conexion.commit()
        conexion.close()

        return redirect("/")

    cursor.execute("SELECT * FROM libros WHERE id = ?", (id,))
    libro = cursor.fetchone()
    conexion.close()

    return render_template("editar.html", libro=libro)


# -----------------------------
# ELIMINAR LIBRO
# -----------------------------
@app.route("/eliminar/<int:id>")
def eliminar(id):
    conexion = sqlite3.connect("biblioteca.db")
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM libros WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()

    return redirect("/")


# -----------------------------
# INICIO
# -----------------------------
@app.route("/")
def index():
    libros = obtener_libros()
    return render_template("index.html", libros=libros)


# -----------------------------
# EJECUTAR
# -----------------------------
if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)