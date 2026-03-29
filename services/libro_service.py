from conexion.conexion import obtener_conexion

def obtener_libros():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM libros")
    datos = cursor.fetchall()
    conexion.close()
    return datos


def insertar_libro(nombre, autor, precio):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO libros (nombre, autor, precio) VALUES (%s,%s,%s)",
        (nombre, autor, precio)
    )
    conexion.commit()
    conexion.close()


def eliminar_libro(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id=%s", (id,))
    conexion.commit()
    conexion.close()