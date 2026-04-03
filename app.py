from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import sqlite3
import io

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "12345"

# -------------------------
# CONEXIÓN SQLITE
# -------------------------
import os

def obtener_conexion():
    db_path = os.path.join(os.getcwd(), "biblioteca.db")
    conexion = sqlite3.connect(db_path)
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
        precio REAL
    )
    """)

    conexion.commit()
    conexion.close()

# -------------------------
# MODELO USUARIO
# -------------------------
class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password

# -------------------------
# LOGIN MANAGER
# -------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

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
# INICIALIZACIÓN (FUNCIONA EN RENDER)
# -------------------------
@app.before_first_request
def inicializar_app():
    crear_tablas()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # CREAR USUARIO SI NO EXISTE
    cursor.execute("SELECT * FROM usuarios WHERE email=?", ("jossel@gmail.com",))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO usuarios (nombre,email,password) VALUES (?,?,?)",
            ("Jossel", "jossel@gmail.com", "1234")
        )

    # CREAR LIBRO DE PRUEBA
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()

    if not libros:
        cursor.execute(
            "INSERT INTO libros (nombre, autor, cantidad, precio) VALUES (?,?,?,?)",
            ("Libro Demo", "Autor Demo", 5, 10.0)
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
            return "Correo o contraseña incorrectos"

    return render_template("login.html")

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
            "INSERT INTO usuarios (nombre,email,password) VALUES (?,?,?)",
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
@app.route("/agregar", methods=["GET","POST"])
@login_required
def agregar():
    if request.method == "POST":
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO libros (nombre,autor,cantidad,precio) VALUES (?,?,?,?)",
            (
                request.form["nombre"],
                request.form["autor"],
                request.form["cantidad"],
                request.form["precio"]
            )
        )

        conexion.commit()
        conexion.close()
        return redirect("/")

    return render_template("agregar.html")

# -------------------------
# EDITAR LIBRO
# -------------------------
@app.route("/editar/<int:id>", methods=["GET","POST"])
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
# ELIMINAR LIBRO
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

    titulo = Paragraph("<font name='Times-Roman' size=18>Reporte de Libros</font>", estilos["Title"])
    elementos.append(titulo)

    datos = [["ID", "Nombre", "Autor", "Cantidad", "Precio"]]

    for libro in libros:
        datos.append([libro["id"], libro["nombre"], libro["autor"], libro["cantidad"], libro["precio"]])

    tabla = Table(datos)
    tabla.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("FONTNAME", (0,0), (-1,-1), "Times-Roman")
    ]))

    elementos.append(tabla)
    pdf.build(elementos)

    buffer.seek(0)
    return make_response(buffer.read())

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)