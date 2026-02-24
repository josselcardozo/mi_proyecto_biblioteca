class Libro:
    def __init__(self, id, nombre, autor, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.autor = autor
        self.cantidad = cantidad
        self.precio = precio

    def actualizar_cantidad(self, nueva_cantidad):
        self.cantidad = nueva_cantidad

    def actualizar_precio(self, nuevo_precio):
        self.precio = nuevo_precio


class Inventario:
    def __init__(self):
        self.libros = {}  # Diccionario

    def agregar_libro(self, libro):
        self.libros[libro.id] = libro

    def eliminar_libro(self, id):
        if id in self.libros:
            del self.libros[id]

    def buscar_por_nombre(self, nombre):
        return [libro for libro in self.libros.values() if nombre.lower() in libro.nombre.lower()]

    def mostrar_todos(self):
        return list(self.libros.values())

    def obtener_autores_unicos(self):
        return {libro.autor for libro in self.libros.values()}