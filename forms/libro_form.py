def validar_libro(nombre, autor, precio):
    if nombre == "" or autor == "" or precio == "":
        return False
    return True