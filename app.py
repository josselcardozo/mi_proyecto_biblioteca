from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import sqlite3
import io
import os
from werkzeug.utils import secure_filename

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------
# APP
# -------------------------
app = Flask(__name__)
app.secret_key = "12345"

# 📸 CARPETA DE IMÁGENES
UPLOAD_FOLDER = 'static/imagenes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------------------
# CONEXIÓN SQLITE
# -------------------------
def obtener_conexion():
    conexion = sqlite3.connect("biblioteca.db")
    conexion.row_factory = sqlite3.Row
    return conexion

# -------------------------
# CREAR TABLAS
# -------------------------
def crear_tablas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS libros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        autor TEXT,
        cantidad INTEGER,
        precio REAL,
        imagen TEXT
    )
    """)

    conexion.commit()
    conexion.close()

# -------------------------
# INICIALIZAR APP
# -------------------------
def inicializar_app():
    crear_tablas()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email=?", ("jossel@gmail.com",))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO usuarios (nombre,email,password) VALUES (?,?,?)",
            ("Jossel", "jossel@gmail.com", "1234")
        )

    conexion.commit()
    conexion.close()

inicializar_app()

# -------------------------
# LOGIN MANAGER
# -------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=?", (user_id,))
    user = cursor.fetchone()
    conexion.close()

    if user:
        return Usuario(user["id_usuario"], user["nombre"], user["email"], user["password"])

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conexion.close()

        if user:
            usuario = Usuario(user["id_usuario"], user["nombre"], user["email"], user["password"])
            login_user(usuario)
            return redirect(url_for("index"))
        else:
            return "❌ Correo o contraseña incorrectos"

    return render_template("login.html")

# -------------------------
# INDEX
# -------------------------
@app.route("/")
@login_required
def index():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    conexion.close()

    return render_template("index.html", libros=libros)

# -------------------------
# AGREGAR LIBRO
# -------------------------
@app.route("/agregar", methods=["GET", "POST"])
@login_required
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        autor = request.form["autor"]
        cantidad = int(request.form["cantidad"])
        precio = float(request.form["precio"])

        imagen = request.files["imagen"]

        if imagen and imagen.filename != "":
            nombre_imagen = secure_filename(imagen.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen)
            imagen.save(ruta)
        else:
            nombre_imagen = "default.jpg"

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO libros (nombre,autor,cantidad,precio,imagen) VALUES (?,?,?,?,?)",
            (nombre, autor, cantidad, precio, nombre_imagen)
        )

        conexion.commit()
        conexion.close()

        return redirect("/")

    return render_template("agregar.html")

# -------------------------
# EDITAR
# -------------------------
@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if request.method == "POST":
        cursor.execute(
            "UPDATE libros SET nombre=?, autor=?, cantidad=?, precio=? WHERE id=?",
            (
                request.form["nombre"],
                request.form["autor"],
                request.form["cantidad"],
                request.form["precio"],
                id
            )
        )
        conexion.commit()
        conexion.close()
        return redirect("/")

    cursor.execute("SELECT * FROM libros WHERE id=?", (id,))
    libro = cursor.fetchone()
    conexion.close()

    return render_template("editar.html", libro=libro)

# -------------------------
# ELIMINAR
# -------------------------
@app.route("/eliminar/<int:id>")
@login_required
def eliminar(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM libros WHERE id=?", (id,))
    conexion.commit()
    conexion.close()

    return redirect("/")

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# -------------------------
# REPORTE PDF
# -------------------------
@app.route("/reporte")
@login_required
def reporte():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    conexion.close()

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    elementos = []
    estilos = getSampleStyleSheet()

    titulo = Paragraph("Reporte de Libros", estilos["Title"])
    elementos.append(titulo)

    datos = [["ID", "Nombre", "Autor", "Cantidad", "Precio"]]

    for libro in libros:
        datos.append([
            libro["id"],
            libro["nombre"],
            libro["autor"],
            libro["cantidad"],
            libro["precio"]
        ])

    tabla = Table(datos)
    tabla.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    elementos.append(tabla)
    pdf.build(elementos)

    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=reporte.pdf"

    return response

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)