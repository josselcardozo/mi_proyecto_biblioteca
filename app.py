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
    libros = Producto.query.all()
    return render_template("index.html", libros=libros)

# -----------------------------
# AGREGAR LIBRO
# -----------------------------
@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form["nombre"]
        autor = request.form["autor"]
        cantidad = int(request.form["cantidad"])
        precio = float(request.form["precio"])

        nuevo_libro = Producto(
            nombre=nombre,
            autor=autor,
            cantidad=cantidad,
            precio=precio
        )

        db.session.add(nuevo_libro)
        db.session.commit()

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
# EJECUTAR
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)