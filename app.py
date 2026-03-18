from flask import Flask, render_template, request, redirect
from conexion.conexion import obtener_conexion

# 🔐 LOGIN
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin

# 📁 ARCHIVOS
from inventario.inventario import (
    guardar_txt, leer_txt,
    guardar_json, leer_json,
    guardar_csv, leer_csv
)

# 🟡 SQLITE
from inventario.bd import db
from inventario.productos import Producto

app = Flask(__name__)
app.secret_key = "12345"

# -----------------------------
# SQLITE CONFIG
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# -----------------------------
# LOGIN CONFIG
# -----------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -----------------------------
# MODELO USUARIO
# -----------------------------
class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password

# -----------------------------
# CARGAR USUARIO (MYSQL)
# -----------------------------
@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (user_id,))
    user = cursor.fetchone()

    conexion.close()

    if user:
        return Usuario(user[0], user[1], user[2], user[3])
    return None

# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        conexion.close()

        if user:
            login_user(Usuario(user[0], user[1], user[2], user[3]))
            return redirect("/")

    return render_template("login.html")

# -----------------------------
# REGISTRO
# -----------------------------
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
            (nombre,email,password)
        )

        conexion.commit()
        conexion.close()

        return redirect("/login")

    return render_template("registro.html")

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# -----------------------------
# MYSQL → LIBROS (PRINCIPAL)
# -----------------------------
@app.route("/")
@login_required
def index():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()

    conexion.close()

    return render_template("index.html", libros=libros)

# -----------------------------
# AGREGAR (MYSQL)
# -----------------------------
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
            (nombre,autor,cantidad,precio)
        )

        conexion.commit()
        conexion.close()

        return redirect("/")

    return render_template("agregar.html")

# -----------------------------
# EDITAR (MYSQL)
# -----------------------------
@app.route("/editar/<int:id>", methods=["GET","POST"])
@login_required
def editar(id):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM libros WHERE id=%s", (id,))
    libro = cursor.fetchone()

    if request.method == "POST":
        nombre = request.form["nombre"]
        autor = request.form["autor"]
        cantidad = request.form["cantidad"]
        precio = request.form["precio"]

        cursor.execute(
            "UPDATE libros SET nombre=%s,autor=%s,cantidad=%s,precio=%s WHERE id=%s",
            (nombre,autor,cantidad,precio,id)
        )

        conexion.commit()
        conexion.close()

        return redirect("/")

    conexion.close()
    return render_template("editar.html", libro=libro)

# -----------------------------
# ELIMINAR (MYSQL)
# -----------------------------
@app.route("/eliminar/<int:id>")
@login_required
def eliminar(id):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM libros WHERE id=%s", (id,))
    conexion.commit()
    conexion.close()

    return redirect("/")

# -----------------------------
# SQLITE → PRODUCTOS
# -----------------------------
@app.route("/productos")
def productos():
    lista = Producto.query.all()
    return render_template("productos.html", productos=lista)

# -----------------------------
# ARCHIVOS TXT/JSON/CSV
# -----------------------------
@app.route("/datos", methods=["GET","POST"])
def datos():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]

        guardar_txt(nombre, precio)
        guardar_json(nombre, precio)
        guardar_csv(nombre, precio)

    return render_template(
        "datos.html",
        datos_txt=leer_txt(),
        datos_json=leer_json(),
        datos_csv=leer_csv()
    )

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)