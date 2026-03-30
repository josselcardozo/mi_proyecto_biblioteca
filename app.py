from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import mysql.connector
from fpdf import FPDF

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "12345"

# -------------------------
# CONEXIÓN MYSQL
# -------------------------
import sqlite3

def obtener_conexion():
    conexion = sqlite3.connect("biblioteca.db")
    conexion.row_factory = sqlite3.Row
    return conexion

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
        precio REAL
    )
    """)

    conexion.commit()
    conexion.close()
    crear_tablas()
crear_admin()
# -------------------------
# MODELOS
# -------------------------
class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password

class Libro:
    def __init__(self, id, nombre, autor, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.autor = autor
        self.cantidad = cantidad
        self.precio = precio

# -------------------------
# LOGIN MANAGER
# -------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (user_id,))
    user = cursor.fetchone()
    conexion.close()

    if user:
        return Usuario(user["id_usuario"], user["nombre"], user["email"], user["password"])

# -------------------------
# CREAR ADMIN
# -------------------------
def crear_admin():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email=%s", ("admin@gmail.com",))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO usuarios (nombre,email,password) VALUES (%s,%s,%s)",
            ("admin", "admin@gmail.com", "1234")
        )
        conexion.commit()

    conexion.close()

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM usuarios WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()
        conexion.close()

        if user:
            usuario = Usuario(
                user["id_usuario"],
                user["nombre"],
                user["email"],
                user["password"]
            )
            login_user(usuario)
            return redirect(url_for("index"))
        else:
            return "Correo o contraseña incorrectos"

    return render_template("login.html")

    @app.route("/reporte")
@login_required
def reporte():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    conexion.close()

    # Crear PDF
    pdf = SimpleDocTemplate("reporte_libros.pdf", pagesize=letter)

    elementos = []

    estilos = getSampleStyleSheet()

    # 🔥 TÍTULO en Times New Roman
    titulo = Paragraph(
        "<font name='Times-Roman' size=18>Reporte de Libros</font>",
        estilos["Title"]
    )

    elementos.append(titulo)

    # TABLA
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

    # ESTILO
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),

        # 🔥 FUENTE TIMES NEW ROMAN
        ("FONTNAME", (0,0), (-1,-1), "Times-Roman"),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    elementos.append(tabla)

    pdf.build(elementos)

    return redirect("/")

# -------------------------
# REGISTRO
# -------------------------
@app.route("/registro", methods=["GET","POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO usuarios (nombre,email,password) VALUES (%s,%s,%s)",
            (nombre, email, password)
        )

        conexion.commit()
        conexion.close()

        return redirect("/login")

    return render_template("registro.html")

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# -------------------------
# INDEX (LISTAR)
# -------------------------
@app.route("/")
@login_required
def index():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM libros")
    datos = cursor.fetchall()
    conexion.close()

    return render_template("index.html", libros=datos)

# -------------------------
# AGREGAR
# -------------------------
@app.route("/agregar", methods=["GET","POST"])
@login_required
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        autor = request.form["autor"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO libros (nombre,autor,cantidad,precio) VALUES (%s,%s,%s,%s)",
            (nombre, autor, cantidad, precio)
        )

        conexion.commit()
        conexion.close()

        return redirect("/")

    return render_template("agregar.html")

# -------------------------
# EDITAR
# -------------------------
@app.route("/editar/<int:id>", methods=["GET","POST"])
@login_required
def editar(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    if request.method == "POST":
        cursor.execute(
            "UPDATE libros SET nombre=%s, autor=%s, cantidad=%s, precio=%s WHERE id=%s",
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

    cursor.execute("SELECT * FROM libros WHERE id=%s", (id,))
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

    cursor.execute("DELETE FROM libros WHERE id=%s", (id,))
    conexion.commit()
    conexion.close()

    return redirect("/")

# -------------------------
# PDF
# -------------------------
from flask import make_response
import io

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

    # TÍTULO
    titulo = Paragraph(
        "<font name='Times-Roman' size=18>Reporte de Libros</font>",
        estilos["Title"]
    )
    elementos.append(titulo)

    # TABLA
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
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("FONTNAME", (0,0), (-1,-1), "Times-Roman"),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    elementos.append(tabla)

    pdf.build(elementos)

    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_libros.pdf'

    return response
# -------------------------
# INICIO
# -------------------------
crear_admin()

if __name__ == "__main__":
    app.run(debug=True)