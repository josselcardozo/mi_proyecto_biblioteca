from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required
from conexion.conexion import obtener_conexion
from models import Usuario, Libro

app = Flask(__name__)
app.secret_key = "12345"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -------------------------
# CARGAR USUARIO
# -------------------------
@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario=%s", (user_id,))
    user = cursor.fetchone()
    conexion.close()

    if user:
        return Usuario(*user)

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

        cursor.execute("SELECT * FROM usuarios WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        conexion.close()

        if user:
            login_user(Usuario(*user))
            return redirect("/")
        else:
            return "Error en login"

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

        cursor.execute("INSERT INTO usuarios (nombre,email,password) VALUES (%s,%s,%s)",
                       (nombre, email, password))
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
# INDEX (PROTEGIDO)
# -------------------------
@app.route("/")
@login_required
def index():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM libros")
    datos = cursor.fetchall()
    conexion.close()

    libros = [Libro(*fila) for fila in datos]

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

        cursor.execute("INSERT INTO libros (nombre,autor,cantidad,precio) VALUES (%s,%s,%s,%s)",
                       (nombre, autor, cantidad, precio))

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
        cursor.execute("UPDATE libros SET nombre=%s,autor=%s,cantidad=%s,precio=%s WHERE id=%s",
                       (request.form["nombre"], request.form["autor"],
                        request.form["cantidad"], request.form["precio"], id))

        conexion.commit()
        conexion.close()
        return redirect("/")

    cursor.execute("SELECT * FROM libros WHERE id=%s", (id,))
    libro = Libro(*cursor.fetchone())
    conexion.close()

    return render_template("editar.html", libro=libro)