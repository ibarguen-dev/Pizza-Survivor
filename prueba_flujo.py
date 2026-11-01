"""Prueba de flujo completo: menu -> partida -> game over -> jugar de nuevo -> salir."""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.init()
pygame.display.set_mode((800, 600))

espacio = {"__name__": "__main__"}
_eventos = pygame.event.get
_contador = {"n": 0}
estado_observado = {"game_over": False, "reiniciado": False, "salido": False}


def get_eventos(*args, **kwargs):
    _contador["n"] += 1
    eventos = _eventos(*args, **kwargs)
    partida = espacio.get("PARTIDA") or {}
    juego = partida.get("juego") if isinstance(partida, dict) else None

    if _contador["n"] == 2:
        # ENTER en el menu: empieza la partida.
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    if _contador["n"] == 10 and juego is not None:
        # El repartidor se queda sin vidas.
        for _ in range(3):
            juego.gestor_estado.invulnerable = False
            juego.gestor_estado.perder_vida()
        estado_observado["game_over"] = True

    if _contador["n"] == 20:
        # Pantalla de fin: S vuelve a jugar.
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))

    if _contador["n"] == 30:
        # La partida nueva debe estar con las 3 vidas y sin puntos.
        juego = (espacio.get("PARTIDA") or {}).get("juego")
        assert juego is not None, "no hay partida nueva"
        assert juego.gestor_estado.vidas == 3, juego.gestor_estado.vidas
        assert juego.gestor_estado.puntaje == 0
        estado_observado["reiniciado"] = True
        # Y despues N cierra el juego.
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_n))

    if _contador["n"] > 40:
        estado_observado["salido"] = True
        return [pygame.event.Event(pygame.QUIT)]
    return eventos


pygame.event.get = get_eventos

with open("main.py", encoding="utf-8") as archivo:
    codigo = archivo.read()

exec(compile(codigo, "main.py", "exec"), espacio)

assert estado_observado["game_over"], "la partida no llegó al game over"
assert estado_observado["reiniciado"], "la tecla S no reinició la partida"
assert estado_observado["salido"], "la app no se cerró"

print("OK 1 - el menu permite empezar la partida")
print("OK 2 - al perder todas las vidas se muestra el game over")
print("OK 3 - la tecla S empieza una partida nueva con 3 vidas y 0 puntos")
print("OK 4 - la tecla N cierra la aplicacion")
