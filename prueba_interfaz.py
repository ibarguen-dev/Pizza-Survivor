"""Pruebas de la interfaz: menu, instrucciones y pantalla de fin de partida."""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.init()
pygame.display.set_mode((800, 600))

from clases.ui import (
    ACCION_INSTRUCCIONES, ACCION_JUGAR, ACCION_REINICIAR, ACCION_SALIR,
    Menu, PantallaFin,
)


def tecla(key):
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def test_menu_inicia_partida():
    menu = Menu()
    assert menu.manejar_evento(tecla(pygame.K_RETURN)) == ACCION_JUGAR
    print("OK 1 - ENTER en la primera opcion empieza la partida")


def test_menu_va_a_instrucciones():
    menu = Menu()
    menu.manejar_evento(tecla(pygame.K_DOWN))
    assert menu.opcion_seleccionada == 1
    accion = menu.manejar_evento(tecla(pygame.K_RETURN))
    assert accion == ACCION_INSTRUCCIONES
    assert menu.mostrando_instrucciones is True
    print("OK 2 - la segunda opcion abre las instrucciones")


def test_instrucciones_vuelven_al_menu():
    menu = Menu()
    menu.manejar_evento(tecla(pygame.K_DOWN))
    menu.manejar_evento(tecla(pygame.K_RETURN))
    menu.manejar_evento(tecla(pygame.K_ESCAPE))
    assert menu.mostrando_instrucciones is False
    print("OK 3 - ESC vuelve al menu principal")


def test_menu_sale_del_juego():
    menu = Menu()
    menu.opcion_seleccionada = 2
    assert menu.manejar_evento(tecla(pygame.K_RETURN)) == ACCION_SALIR
    print("OK 4 - la ultima opcion cierra el juego")


def test_instrucciones_se_desplazan():
    menu = Menu()
    menu.mostrando_instrucciones = True
    assert menu.desplazamiento_maximo() > 0, "debe haber contenido que desplazar"
    menu.manejar_evento(tecla(pygame.K_DOWN))
    assert menu.desplazamiento > 0
    menu.manejar_evento(tecla(pygame.K_END))
    assert menu.desplazamiento == menu.desplazamiento_maximo()
    menu.manejar_evento(tecla(pygame.K_HOME))
    assert menu.desplazamiento == 0
    print("OK 5 - las instrucciones se desplazan con las flechas")


def test_dibujo_de_la_interfaz():
    menu = Menu()
    pantalla = pygame.Surface((800, 600))
    menu.dibujar(pantalla)
    menu.mostrando_instrucciones = True
    menu.desplazamiento = menu.desplazamiento_maximo()
    menu.dibujar(pantalla)
    fin = PantallaFin(puntaje=42, tiempo_ms=65000, mejor_puntaje=100)
    fin.dibujar(pantalla)
    print("OK 6 - menu, instrucciones y fin de partida se dibujan sin errores")


def test_pantalla_fin_s_y_n():
    fin = PantallaFin(puntaje=10, tiempo_ms=1000)
    assert fin.manejar_evento(tecla(pygame.K_s)) == ACCION_REINICIAR
    assert fin.manejar_evento(tecla(pygame.K_n)) == ACCION_SALIR
    assert fin.manejar_evento(tecla(pygame.K_x)) is None
    print("OK 7 - S vuelve a jugar y N cierra el juego")


def test_mouse_selecciona_opciones():
    menu = Menu()
    rect = menu._rects_opciones()[2]
    evento = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)
    assert menu.manejar_evento(evento) == ACCION_SALIR
    print("OK 8 - las opciones tambien se pueden pulsar con el raton")


if __name__ == "__main__":
    test_menu_inicia_partida()
    test_menu_va_a_instrucciones()
    test_instrucciones_vuelven_al_menu()
    test_menu_sale_del_juego()
    test_instrucciones_se_desplazan()
    test_dibujo_de_la_interfaz()
    test_pantalla_fin_s_y_n()
    test_mouse_selecciona_opciones()
    print("\nTodas las pruebas de interfaz pasaron.")
