"""Pruebas funcionales del sistema de super poderes."""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.init()
pygame.mixer.init()

from clases.gestor_estado import GestorEstado
from clases.gestor_poderes import GestorPoderes, Poder
from clases.gestor_enemigos import GestorEnemigos
from clases.perro import Perro
from clases.repartidor import Repartidor
from clases.recogible import Recogible
from clases.config import TIPO_ORBITA, TIPO_PERFORANTE, TIPO_VIDA


def nuevo_contexto():
    repartidor = Repartidor(368, 440, "assets/imagenes/repartidor.png")
    gestor_enemigos = GestorEnemigos()
    gestor_enemigos.agregar_tipo(Perro, 999999)
    gestor_enemigos.enemigos.clear()
    estado = GestorEstado()
    poderes = GestorPoderes(estado)
    return repartidor, gestor_enemigos, estado, poderes


def test_recogida_por_contacto():
    repartidor, ge, estado, gp = nuevo_contexto()
    gp.recogibles.clear()
    gp.recogibles.append(Recogible(TIPO_PERFORANTE, repartidor.x, repartidor.y))
    gp.actualizar(pygame.time.get_ticks(), repartidor, ge)
    assert len(gp.poderes) == 1, gp.poderes
    assert gp.poderes[0].tipo == TIPO_PERFORANTE
    assert gp.poderes[0].cargas == 3
    assert len(gp.recogibles) == 0
    print("OK 1 - recogida por contacto: poder con 3 cargas")


def test_cola_de_poderes():
    repartidor, ge, estado, gp = nuevo_contexto()
    gp._recolectar(Recogible(TIPO_PERFORANTE))
    gp._recolectar(Recogible(TIPO_ORBITA))
    assert [p.tipo for p in gp.poderes] == [TIPO_PERFORANTE, TIPO_ORBITA]
    # Solo se gasta el primero que se agarró.
    gp.usar(repartidor, ge)
    assert gp.poderes[0].tipo == TIPO_PERFORANTE and gp.poderes[0].cargas == 2
    assert gp.poderes[1].tipo == TIPO_ORBITA and gp.poderes[1].cargas == 3
    # Agotar el primero hace que el segundo sea el activo.
    gp.usar(repartidor, ge)
    gp.usar(repartidor, ge)
    assert [p.tipo for p in gp.poderes] == [TIPO_ORBITA]
    print("OK 2 - cola: se gasta el primero, luego el segundo")


def test_recarga_parcial():
    repartidor, ge, estado, gp = nuevo_contexto()
    gp._recolectar(Recogible(TIPO_PERFORANTE))
    gp.usar(repartidor, ge)   # queda con 2 cargas
    assert gp.poderes[0].cargas == 2
    gp._recolectar(Recogible(TIPO_PERFORANTE))
    assert gp.poderes[0].cargas == 3, "debe restaurar lo que falta"
    assert estado.vidas == 3, "no debe dar vida si no estaba lleno"
    print("OK 3 - recarga parcial: 2 -> 3 cargas, sin vida extra")


def test_poder_lleno_da_vida_extra():
    repartidor, ge, estado, gp = nuevo_contexto()
    gp._recolectar(Recogible(TIPO_PERFORANTE))
    gp._recolectar(Recogible(TIPO_PERFORANTE))
    assert estado.vidas == 4, estado.vidas
    print("OK 4 - poder ya lleno da vida extra (3 -> 4 vidas)")


def test_corazon_da_vida():
    repartidor, ge, estado, gp = nuevo_contexto()
    gp._recolectar(Recogible(TIPO_VIDA))
    assert estado.vidas == 4
    for _ in range(10):
        gp._recolectar(Recogible(TIPO_VIDA))
    assert estado.vidas == 5, estado.vidas
    print("OK 5 - corazón da vida, con tope máximo de 5")


def test_onda_perforante_atraviesa_varios():
    repartidor, ge, estado, gp = nuevo_contexto()
    cx, cy = repartidor.obtener_centro()
    # 4 enemigos en la línea de tiro (horizontal, a la derecha).
    for i in range(4):
        enemigo = Perro.__new__(Perro)
        enemigo.x = cx + 80 + i * 70 - 27
        enemigo.y = cy - 32
        enemigo.velocidad = 0.5
        ge.enemigos.append(enemigo)
    gp.poderes.append(Poder(TIPO_PERFORANTE))
    gp.usar(repartidor, ge)
    assert len(gp.ondas) == 1
    for _ in range(200):
        gp.actualizar(pygame.time.get_ticks(), repartidor, ge)
    assert len(ge.enemigos) == 0, f"debería eliminar a todos, quedan {len(ge.enemigos)}"
    print("OK 6 - onda perforante atraviesa y elimina a varios enemigos")


def test_onda_desaparece_fuera_de_pantalla():
    repartidor, ge, estado, gp = nuevo_contexto()
    gp.poderes.append(Poder(TIPO_PERFORANTE))
    gp.usar(repartidor, ge)
    for _ in range(600):
        gp.actualizar(pygame.time.get_ticks(), repartidor, ge)
    assert len(gp.ondas) == 0, "la onda debe desaparecer al salir de la pantalla"
    print("OK 7 - onda desaparece cuando ya no es visible en pantalla")


def test_orbita_protege_tres_ataques():
    repartidor, ge, estado, gp = nuevo_contexto()
    gp.poderes.append(Poder(TIPO_ORBITA))
    gp.usar(repartidor, ge)
    assert gp.orbita is not None
    assert gp.orbita.protecciones == 3
    for i in range(3):
        assert gp.proteger_ataque() is True, f"ataque {i+1} debió ser absorbido"
    assert gp.orbita is None, "la órbita debe terminar tras 3 ataques"
    assert gp.proteger_ataque() is False
    assert estado.vidas == 3, "el repartidor no debe perder vidas"
    print("OK 8 - órbita salva de 3 ataques y luego desaparece")


def test_orbita_gira_alrededor():
    repartidor, ge, estado, gp = nuevo_contexto()
    gp.poderes.append(Poder(TIPO_ORBITA))
    gp.usar(repartidor, ge)
    cx, cy = repartidor.obtener_centro()
    posiciones = set()
    for _ in range(30):
        gp.actualizar(pygame.time.get_ticks(), repartidor, ge)
        posiciones.add((round(gp.orbita.x), round(gp.orbita.y)))
    assert len(posiciones) > 5, "la órbita debe moverse"
    dist = ((gp.orbita.x - cx) ** 2 + (gp.orbita.y - cy) ** 2) ** 0.5
    assert 50 < dist < 80, f"radio inesperado: {dist}"
    print("OK 9 - órbita gira alrededor del repartidor")


def test_hud_inventario():
    repartidor, ge, estado, gp = nuevo_contexto()
    pantalla = pygame.Surface((800, 600))
    gp.poderes.append(Poder(TIPO_PERFORANTE))
    gp.poderes.append(Poder(TIPO_ORBITA))
    gp.dibujar_inventario(pantalla)
    assert pantalla.get_at((15, 60)) != (0, 0, 0), "debe dibujar el icono del poder"
    print("OK 10 - inventario se dibuja bajo las vidas")


if __name__ == "__main__":
    test_recogida_por_contacto()
    test_cola_de_poderes()
    test_recarga_parcial()
    test_poder_lleno_da_vida_extra()
    test_corazon_da_vida()
    test_onda_perforante_atraviesa_varios()
    test_onda_desaparece_fuera_de_pantalla()
    test_orbita_protege_tres_ataques()
    test_orbita_gira_alrededor()
    test_hud_inventario()
    print("\nTodas las pruebas pasaron.")
