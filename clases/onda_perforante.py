import math

import pygame

from clases.config import (
    ANCHO_PANTALLA, ALTO_PANTALLA,
    RADIO_PERFORANTE, VELOCIDAD_PERFORANTE,
)
from clases.rutas import resolver


class OndaPerforante:
    """Super poder 1: onda que atraviesa a varios enemigos al mismo tiempo.

    No se destruye al primer impacto: sigue su curso eliminando a todos los
    enemigos que encuentra y desaparece al salir de la pantalla.
    """

    ANCHO = 44
    ALTO = 48

    def __init__(self, x, y, direccion_x, direccion_y):
        self.x = x
        self.y = y
        self.dx = direccion_x * VELOCIDAD_PERFORANTE
        self.dy = direccion_y * VELOCIDAD_PERFORANTE
        self.x_previo = x
        self.y_previo = y
        # True cuando el poder desaparece al chocar contra un jefe.
        self.consumida = False
        self.imagen = pygame.transform.scale(
            pygame.image.load(resolver("assets/imagenes/super_poder_1.png")),
            (self.ANCHO, self.ALTO),
        )

    def mover(self):
        self.x_previo = self.x
        self.y_previo = self.y
        self.x += self.dx
        self.y += self.dy

    def esta_fuera_de_pantalla(self):
        return (self.x < -self.ANCHO or self.x > ANCHO_PANTALLA or
                self.y < -self.ALTO or self.y > ALTO_PANTALLA)

    def _distancia_al_segmento(self, px, py):
        """Distancia de un punto al segmento recorrido por la onda en este frame.

        Devuelve (distancia, t), donde t es la posición del punto sobre el
        segmento (0 al principio, 1 al final). Sirve para saber a quién
        tocó la onda primero.
        """
        x1, y1 = self.x_previo + self.ANCHO // 2, self.y_previo + self.ALTO // 2
        x2, y2 = self.x + self.ANCHO // 2, self.y + self.ALTO // 2
        dx, dy = x2 - x1, y2 - y1
        largo = dx * dx + dy * dy
        if largo == 0:
            return math.hypot(px - x2, py - y2), 0.0
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / largo))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy)), t

    def eliminar_enemigos(self, gestor_enemigos):
        """Elimina a los enemigos que la onda toca. Devuelve cuántos eliminó.

        Si el primer enemigo que toca es un jefe, el poder desaparece y le
        quita una vida entera.
        """
        tocados = []
        for enemigo in list(gestor_enemigos.enemigos):
            ex, ey = enemigo.obtener_centro()
            distancia, t = self._distancia_al_segmento(ex, ey)
            if distancia < RADIO_PERFORANTE:
                tocados.append((t, enemigo))
        tocados.sort(key=lambda item: item[0])

        eliminados = 0
        for _, enemigo in tocados:
            if enemigo.es_jefe:
                # El poder desaparece al tocar al jefe y le quita una vida.
                enemigo.perder_vida_directa()
                self.consumida = True
                break
            if enemigo.recibir_dano(1):
                gestor_enemigos.enemigos.remove(enemigo)
                eliminados += 1
        return eliminados

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, (self.x, self.y))
