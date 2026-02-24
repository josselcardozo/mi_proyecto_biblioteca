import sqlite3

def conectar():
    return sqlite3.connect("inventario.db")

def crear_tabla():
    conexion = conectar()
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

def insertar_libro(nombre, autor, cantidad, precio):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO libros (nombre, autor, cantidad, precio)
        VALUES (?, ?, ?, ?)
    """, (nombre, autor, cantidad, precio))

    conexion.commit()
    conexion.close()


def obtener_libros():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()
    conexion.close()
    return libros


def eliminar_libro(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()


def actualizar_libro(id, cantidad, precio):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE libros
        SET cantidad = ?, precio = ?
        WHERE id = ?
    """, (cantidad, precio, id))
    conexion.commit()
    conexion.close()