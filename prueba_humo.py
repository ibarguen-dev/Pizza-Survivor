"""Prueba de humo: ejecuta el bucle real de main.py con jefes y pizzas activas."""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

# Aceleramos los tiempos para que todo pase dentro de la prueba.
import clases.gestor_jefes as gestor_jefes_mod
import clases.jefe as jefe_mod
import clases.jefe_perro as jefe_perro_mod
import clases.gestor_pizzas as gestor_pizzas_mod
from clases.jefe_perro import JefePerro

gestor_jefes_mod.INTERVALO_APARICION_JEFE = 50
jefe_mod.INTERVALO_ATAQUE_JEFE = 50
jefe_perro_mod.INTERVALO_INVOCACION_JEFE = 50
gestor_pizzas_mod.INTERVALO_RECARGA_PIZZA = 100
# En esta prueba sale siempre el perro zombi (el que invoca la jauría).
gestor_jefes_mod.GestorJefes.TIPOS_JEFE = (JefePerro,)

espacio = {"__name__": "__main__"}
_eventos = pygame.event.get
_contador = {"n": 0}
muestras = {"pizzas": [], "jauria": 0}


def get_eventos(*args, **kwargs):
    _contador["n"] += 1
    eventos = _eventos(*args, **kwargs)
    if _contador["n"] == 2:
        # ENTER en el menu: empieza la partida.
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    if _contador["n"] == 20:
        # El repartidor lanza una pizza manual con la tecla E.
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
    if _contador["n"] == 40:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    partida = espacio.get("PARTIDA") or {}
    juego = partida.get("juego") if isinstance(partida, dict) else None
    if juego is not None:
        muestras["pizzas"].append(juego.gestor_pizzas.disponibles)
        muestras["jauria"] = max(muestras["jauria"], sum(
            1 for e in juego.gestor_enemigos.enemigos if getattr(e, "es_jauria", False)
        ))
    if _contador["n"] > 400:
        return [pygame.event.Event(pygame.QUIT)]
    return eventos


pygame.event.get = get_eventos

with open("main.py", encoding="utf-8") as archivo:
    codigo = archivo.read()

exec(compile(codigo, "main.py", "exec"), espacio)

juego = espacio["PARTIDA"]["juego"]
assert juego is not None, "no se pudo empezar la partida desde el menu"

gestor_jefes = juego.gestor_jefes
gestor_pizzas = juego.gestor_pizzas
gestor_enemigos = juego.gestor_enemigos

assert len(gestor_jefes.jefes) >= 1, "no apareció ningún jefe"
jefe = gestor_jefes.jefes[0]
assert muestras["jauria"] > 0, "el jefe no invocó ninguna jauría"
assert min(muestras["pizzas"]) < 5, "la pizza manual nunca llegó a dispararse"

print("OK - el bucle del juego se ejecutó 400 frames sin errores")
print(f"OK - jefe en pantalla: {jefe.nombre} con {jefe.vidas} vidas")
print(f"OK - jauría invocada: {muestras['jauria']} perros a la vez")
print(f"OK - pizzas manuales usadas: {5 - min(muestras['pizzas'])} de 5")
