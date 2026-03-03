import os
import json
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

TXT_FILE = os.path.join(DATA_DIR, "datos.txt")
JSON_FILE = os.path.join(DATA_DIR, "datos.json")
CSV_FILE = os.path.join(DATA_DIR, "datos.csv")


# ---------------- TXT ----------------
def guardar_txt(nombre, precio):
    with open(TXT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nombre},{precio}\n")


def leer_txt():
    datos = []
    if os.path.exists(TXT_FILE):
        with open(TXT_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                datos.append(linea.strip().split(","))
    return datos


# ---------------- JSON ----------------
def guardar_json(nombre, precio):
    nuevo = {"nombre": nombre, "precio": precio}
    datos = []

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except:
                datos = []

    datos.append(nuevo)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)


def leer_json():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []


# ---------------- CSV ----------------
def guardar_csv(nombre, precio):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nombre, precio])


def leer_csv():
    datos = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for fila in reader:
                datos.append(fila)
    return datos