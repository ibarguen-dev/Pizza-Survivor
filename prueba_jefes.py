"""Pruebas funcionales de los jefes, la jauría y las pizzas manuales."""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.init()
pygame.display.set_mode((800, 600))

from clases.config import (
    CANTIDAD_JAURIA, DURACION_IRA_ZOMBIE, IMPACTOS_POR_VIDA_JEFE,
    INTERVALO_INVOCACION_JEFE, INTERVALO_RECARGA_PIZZA,
    PIZZAS_MANUALES_MAXIMAS, VELOCIDAD_JAURIA, VIDAS_JEFE,
)
from clases.gestor_enemigos import GestorEnemigos
from clases.gestor_estado import GestorEstado
from clases.gestor_jefes import GestorJefes
from clases.gestor_poderes import GestorPoderes, Poder
from clases.gestor_pizzas import GestorPizzas
from clases.jefe_perro import JefePerro
from clases.jefe_zombie import JefeZombie
from clases.perro import Perro
from clases.repartidor import Repartidor
from clases.rutas import resolver


def nuevo_contexto():
    repartidor = Repartidor(368, 440, "assets/imagenes/repartidor.png")
    gestor_enemigos = GestorEnemigos()
    gestor_jefes = GestorJefes(gestor_enemigos)
    gestor_pizzas = GestorPizzas()
    estado = GestorEstado()
    poderes = GestorPoderes(estado)
    return repartidor, gestor_enemigos, gestor_jefes, gestor_pizzas, estado, poderes


def test_jefe_tiene_cinco_vidas():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    jefe = JefePerro()
    assert jefe.vidas == VIDAS_JEFE == 5, jefe.vidas
    assert jefe.es_jefe
    print("OK 1 - el jefe tiene 5 vidas")


def test_tres_impactos_quitan_una_vida():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    jefe = JefePerro()
    jefe.recibir_dano(1)
    jefe.recibir_dano(1)
    assert jefe.vidas == 5, "con 2 impactos sigue con 5 vidas"
    assert jefe.impactos == 2
    jefe.recibir_dano(1)
    assert jefe.vidas == 4, "el tercer impacto quita una vida"
    assert jefe.impactos == 0
    print("OK 2 - 3 impactos quitan una vida del jefe")


def test_poder_1_quita_una_vida_al_jefe():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    jefe = JefePerro()
    jefe.x, jefe.y = repartidor.obtener_centro()
    ge.enemigos.append(jefe)
    poderes.poderes.append(Poder("perforante"))
    poderes.usar(repartidor, ge)
    assert len(poderes.ondas) == 1
    for _ in range(200):
        poderes.actualizar(pygame.time.get_ticks(), repartidor, ge)
    assert jefe.vidas == 4, f"el poder 1 debe quitar una vida, quedan {jefe.vidas}"
    assert len(poderes.ondas) == 0, "el poder desaparece al tocar al jefe"
    print("OK 3 - el poder 1 quita una vida y desaparece al tocar al jefe")


def test_pizza_manual_sin_jefe_no_se_lanza():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    assert gj.hay_jefe() is False
    assert gp.lanzar(repartidor, gj) is False
    assert gp.disponibles == PIZZAS_MANUALES_MAXIMAS, "no debe gastar munición"
    print("OK 4 - sin jefe la pizza manual no se lanza ni se consume")


def test_pizza_manual_va_al_jefe():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    jefe = JefePerro()
    jefe.x, jefe.y = 100, 100
    gj.jefes.append(jefe)
    ge.enemigos.append(jefe)
    assert gp.lanzar(repartidor, gj) is True
    assert gp.disponibles == PIZZAS_MANUALES_MAXIMAS - 1
    assert len(gp.pizzas) == 1
    print("OK 5 - la pizza manual se lanza al jefe y gasta munición")


def test_pizza_manual_se_pierde_con_enemigo_comun():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    jefe = JefePerro()
    jefe.x, jefe.y = 100, 100
    gj.jefes.append(jefe)
    ge.enemigos.append(jefe)
    # Enemigo común justo en mitad del camino entre el repartidor y el jefe.
    cx, cy = repartidor.obtener_centro()
    comun = Perro()
    comun.x = (cx + 155) // 2 - comun.ancho // 2
    comun.y = (cy + 160) // 2 - comun.alto // 2
    ge.enemigos.append(comun)
    gp.lanzar(repartidor, gj)
    for _ in range(60):
        gp.actualizar(pygame.time.get_ticks(), ge)
    assert len(gp.pizzas) == 0, "la pizza se pierde al tocar un enemigo común"
    assert comun.vidas == 1, "el enemigo común no recibe daño"
    assert jefe.vidas == 5, "la pizza no debe haber alcanzado al jefe"
    print("OK 6 - un enemigo común hace perder la pizza sin dañarlo")


def test_recarga_de_pizzas():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    gp.disponibles = 0
    gp.ultima_recarga = pygame.time.get_ticks() - INTERVALO_RECARGA_PIZZA
    gp.actualizar(pygame.time.get_ticks(), ge)
    assert gp.disponibles == 1, gp.disponibles
    gp.actualizar(pygame.time.get_ticks(), ge)
    assert gp.disponibles == 1, "no se recarga antes de tiempo"
    print("OK 7 - las pizzas se recuperan cada 3,5 segundos")


def test_zombie_alterna_ira_y_descanso():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    jefe = JefeZombie()
    assert jefe.en_ira is True
    jefe.tiempo_estado = pygame.time.get_ticks() - DURACION_IRA_ZOMBIE
    jefe.actualizar_movimiento(*repartidor.obtener_centro())
    assert jefe.en_ira is False, "tras la ira debe descansar"
    jefe.tiempo_estado = pygame.time.get_ticks() - 3000
    jefe.actualizar_movimiento(*repartidor.obtener_centro())
    assert jefe.en_ira is True, "tras el descanso vuelve a la ira"
    print("OK 8 - el zombie alterna entre la ira y el descanso")


def test_perro_zombie_invoca_jauria():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    jefe = JefePerro()
    jefe.tiempo_invocacion = pygame.time.get_ticks() - INTERVALO_INVOCACION_JEFE
    antes = len(ge.enemigos)
    jefe.actualizar_comportamiento(pygame.time.get_ticks(), repartidor, ge)
    jauria = [e for e in ge.enemigos if getattr(e, "es_jauria", False)]
    assert len(jauria) == CANTIDAD_JAURIA, len(jauria)
    assert len(ge.enemigos) == antes + CANTIDAD_JAURIA
    print("OK 9 - el perro zombi invoca una jauría de perros")


def test_jauria_no_persigue():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    from clases.jauria import Jauria
    perro = Jauria(repartidor.obtener_centro()[0], repartidor.obtener_centro()[1])
    paso = (perro.dx, perro.dy)
    x_inicial, y_inicial = perro.x, perro.y
    # Aunque el repartidor se mueva, el perro no corrige su rumbo.
    perro.actualizar_movimiento(0, 0)
    perro.actualizar_movimiento(0, 0)
    assert (perro.dx, perro.dy) == paso, "la jauría no puede cambiar de dirección"
    assert abs((perro.x - x_inicial) - paso[0] * 2) < 0.001
    assert abs((perro.y - y_inicial) - paso[1] * 2) < 0.001
    assert abs(paso[0]) <= VELOCIDAD_JAURIA + 0.001
    print("OK 10 - los perros de la jauría se mueven en línea recta")


def test_jefe_no_se_elimina_al_tocar_al_repartidor():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    jefe = JefePerro()
    jefe.x = repartidor.obtener_centro()[0] - jefe.ancho // 2
    jefe.y = repartidor.obtener_centro()[1] - jefe.alto // 2
    ge.enemigos.append(jefe)
    golpes = ge.detectar_colision_repartidor(repartidor)
    assert golpes == 1, "el jefe debe contar como un golpe"
    assert jefe in ge.enemigos, "el jefe no debe eliminarse al tocar al repartidor"
    print("OK 11 - el jefe golpea pero no desaparece al tocar al repartidor")


def test_barra_de_vida_solo_con_jefe():
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    pantalla = pygame.Surface((800, 600))
    gj.dibujar_barras_vida(pantalla)
    assert pantalla.get_at((210, 70))[:3] == (0, 0, 0), "sin jefe no hay barra de vida"
    jefe = JefePerro()
    gj.jefes.append(jefe)
    gj.dibujar_barras_vida(pantalla)
    assert pantalla.get_at((210, 70))[:3] != (0, 0, 0), "con jefe debe verse la barra"
    print("OK 12 - la barra de vida del jefe solo aparece cuando sale")


def test_vidas_del_jefe_con_la_imagen_de_cabeza():
    """Las vidas se muestran con la imagen head: una por cada vida."""
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    jefe = JefePerro()
    gj.jefes.append(jefe)
    pantalla = pygame.Surface((800, 600))
    gj.dibujar_barras_vida(pantalla)
    x = gj.X_VIDAS + 2
    y = gj.Y_VIDAS + gj.TAMANO_VIDA // 2
    assert pantalla.get_at((x, y))[:3] != (0, 0, 0), "debe verse la cabeza del jefe"
    # Con menos vidas, la última cabeza se apaga.
    jefe.vidas = 2
    pantalla2 = pygame.Surface((800, 600))
    gj.dibujar_barras_vida(pantalla2)
    x_ultima = gj.X_VIDAS + 4 * (gj.TAMANO_VIDA + gj.SEPARACION_VIDA) + 2
    assert pantalla2.get_at((x_ultima, y))[:3] != (0, 0, 0), "la cabeza sigue dibujada"
    print("OK 14 - las vidas del jefe se muestran con la imagen de cabeza")


def test_cabeza_del_jefe_esta_reflejada():
    """La cabeza debe ser similar a la del repartidor pero al lado contrario."""
    from clases.recursos import imagen_cabeza_jefe
    repartidor = pygame.image.load(
        resolver("assets/imagenes/repartidor.png")
    ).convert_alpha()
    w, h = repartidor.get_size()
    alto = int(h * 0.16)
    ancho = min(w, alto)
    recorte = repartidor.subsurface(
        pygame.Rect((w - ancho) // 2, 0, ancho, alto)
    )
    esperado = pygame.transform.scale(
        pygame.transform.flip(recorte, True, False), (36, 36)
    )
    cabeza = imagen_cabeza_jefe(36, 36)
    for x in range(0, 36, 4):
        for y in range(0, 36, 4):
            assert cabeza.get_at((x, y)) == esperado.get_at((x, y)), \
                "la cabeza debe ser el recorte del repartidor reflejado"
    print("OK 15 - la cabeza del jefe es el recorte del repartidor reflejado")


def test_jefe_aparece_cada_cinco_minutos():
    from clases.config import INTERVALO_APARICION_JEFE
    repartidor, ge, gj, gp, estado, poderes = nuevo_contexto()
    gj.tiempo_ultimo_jefe = pygame.time.get_ticks() - INTERVALO_APARICION_JEFE
    gj._gestionar_spawn(pygame.time.get_ticks())
    assert len(gj.jefes) == 1, "debe aparecer un jefe a los 5 minutos"
    assert gj.jefes[0] in ge.enemigos
    print("OK 13 - un jefe aparece cada 5 minutos")


if __name__ == "__main__":
    test_jefe_tiene_cinco_vidas()
    test_tres_impactos_quitan_una_vida()
    test_poder_1_quita_una_vida_al_jefe()
    test_pizza_manual_sin_jefe_no_se_lanza()
    test_pizza_manual_va_al_jefe()
    test_pizza_manual_se_pierde_con_enemigo_comun()
    test_recarga_de_pizzas()
    test_zombie_alterna_ira_y_descanso()
    test_perro_zombie_invoca_jauria()
    test_jauria_no_persigue()
    test_jefe_no_se_elimina_al_tocar_al_repartidor()
    test_barra_de_vida_solo_con_jefe()
    test_vidas_del_jefe_con_la_imagen_de_cabeza()
    test_cabeza_del_jefe_esta_reflejada()
    test_jefe_aparece_cada_cinco_minutos()
    print("\nTodas las pruebas de jefes pasaron.")
