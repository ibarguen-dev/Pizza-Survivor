"""Resolución de rutas de los recursos del juego.

El juego carga imágenes y sonidos que viven dentro de la carpeta 'assets'.
Desde el código fuente bastan rutas relativas, pero el ejecutable generado
con PyInstaller no las usa: los recursos se extraen a una carpeta temporal
(`sys._MEIPASS`) y el directorio de trabajo puede ser cualquiera. Por eso
todas las rutas se resuelven aquí, de forma absoluta.
"""
import os
import sys


def _carpetas_candidatas():
    """Carpetas donde pueden estar los recursos, en orden de prioridad."""
    candidatas = []
    if getattr(sys, "frozen", False):
        # PyInstaller extrae los datos empaquetados en _MEIPASS.
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidatas.append(meipass)
        carpeta_exe = os.path.dirname(os.path.abspath(sys.executable))
        candidatas.append(carpeta_exe)
        candidatas.append(os.path.join(carpeta_exe, "_internal"))
    else:
        # Carpeta raíz del proyecto: el padre del paquete 'clases'.
        candidatas.append(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    return candidatas


def _encontrar_base():
    """Primera carpeta candidata que contiene la carpeta 'assets'."""
    candidatas = _carpetas_candidatas()
    for carpeta in candidatas:
        if os.path.isdir(os.path.join(carpeta, "assets")):
            return carpeta
    # Si no se encuentra, se devuelve la primera candidata: al menos la ruta
    # del error será clara.
    return candidatas[0]


BASE_DIR = _encontrar_base()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGENES_DIR = os.path.join(ASSETS_DIR, "imagenes")
SONIDOS_DIR = os.path.join(ASSETS_DIR, "mp3")


def imagen(nombre):
    """Ruta absoluta de una imagen de 'assets/imagenes'."""
    return os.path.join(IMAGENES_DIR, nombre)


def sonido(nombre):
    """Ruta absoluta de un sonido de 'assets/mp3'."""
    return os.path.join(SONIDOS_DIR, nombre)


def resolver(ruta):
    """Convierte una ruta relativa de 'assets' en una ruta absoluta.

    Las rutas que ya son absolutas se devuelven sin tocar, de modo que la
    función también sirve para rutas fijadas en el código.
    """
    if os.path.isabs(ruta):
        return ruta
    normalizada = ruta.replace("\\", "/")
    if normalizada.startswith("assets/"):
        return os.path.join(BASE_DIR, *normalizada.split("/"))
    return os.path.join(BASE_DIR, *normalizada.split("/"))
