import math
import random

import pygame

from clases.config import (
    TIPO_ORBITA, TIPO_PERFORANTE, TIPO_VIDA,
    ANCHO_PANTALLA, ALTO_PANTALLA,
    DURACION_RECOGIBLE, VELOCIDAD_RECOGIBLE,
)
from clases.rutas import resolver

RUTAS_IMAGEN = {
    TIPO_PERFORANTE: "assets/imagenes/super_poder_1.png",
    TIPO_ORBITA: "assets/imagenes/super_poder_2.png",
    TIPO_VIDA: "assets/imagenes/corazon.png",
}


class Recogible:
    """Ítem que aparece en pantalla y que el repartidor debe tocar para obtenerlo."""

    ANCHO = 44
    ALTO = 44

    def __init__(self, tipo, x=None, y=None):
        self.tipo = tipo
        self.imagen = pygame.transform.scale(
            pygame.image.load(resolver(RUTAS_IMAGEN[tipo])), (self.ANCHO, self.ALTO)
        )
        if x is None:
            x = random.randint(0, ANCHO_PANTALLA - self.ANCHO)
        if y is None:
            y = random.randint(0, ALTO_PANTALLA - self.ALTO)
        self.x = x
        self.y = y
        self.velocidad = VELOCIDAD_RECOGIBLE
        self.angulo = random.uniform(0, math.tau)
        self.tiempo_inicio = pygame.time.get_ticks()
        self.tiempo_fin = self.tiempo_inicio + DURACION_RECOGIBLE

    def mover(self):
        """Desplazamiento lento en diagonal, rebotando en los bordes de la pantalla."""
        self.x += math.cos(self.angulo) * self.velocidad
        self.y += math.sin(self.angulo) * self.velocidad
        if self.x < 0 or self.x > ANCHO_PANTALLA - self.ANCHO:
            self.angulo = math.pi - self.angulo
            self.x = max(0, min(self.x, ANCHO_PANTALLA - self.ANCHO))
        if self.y < 0 or self.y > ALTO_PANTALLA - self.ALTO:
            self.angulo = -self.angulo
            self.y = max(0, min(self.y, ALTO_PANTALLA - self.ALTO))

    def esta_expirado(self, tiempo_actual):
        return tiempo_actual >= self.tiempo_fin

    def colisiona_con(self, x, y, radio):
        cx = self.x + self.ANCHO // 2
        cy = self.y + self.ALTO // 2
        return math.hypot(cx - x, cy - y) < radio

    def dibujar(self, pantalla):
        """Parpadea durante los últimos 3 segundos antes de desaparecer."""
        restante = self.tiempo_fin - pygame.time.get_ticks()
        if restante < 3000 and (restante // 250) % 2 == 0:
            return
        pantalla.blit(self.imagen, (self.x, self.y))
