from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import sqlite3

app = Flask(__name__)
app.secret_key = "12345"

# -------------------------
# CONEXIÓN DB
# -------------------------
def obtener_conexion():
    conexion = sqlite3.connect("database.db")
    conexion.row_factory = sqlite3.Row
    return conexion

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
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=?", (user_id,))
    user = cursor.fetchone()
    conexion.close()

    if user:
        return Usuario(user["id_usuario"], user["nombre"], user["email"], user["password"])

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
# CREAR ADMIN AUTOMÁTICO
# -------------------------
def crear_admin():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # 🔥 BORRA SI EXISTE
    cursor.execute("DELETE FROM usuarios WHERE email=?", ("jossel@gmail.com",))

    # 🔥 CREA SIEMPRE
    cursor.execute(
        "INSERT INTO usuarios (nombre,email,password) VALUES (?,?,?)",
        ("jossel", "jossel@gmail.com", "1234")
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
    datos = cursor.fetchall()
    conexion.close()

    libros = [
        Libro(fila["id"], fila["nombre"], fila["autor"], fila["cantidad"], fila["precio"])
        for fila in datos
    ]

    return render_template("index.html", libros=libros)

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
            "INSERT INTO libros (nombre,autor,cantidad,precio) VALUES (?,?,?,?)",
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
# INICIO
# -------------------------
crear_tablas()
crear_admin()

if __name__ == "__main__":
    app.run(debug=True)