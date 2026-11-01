import math

import pygame

from clases.config import (
    ANCHO_PANTALLA, ALTO_PANTALLA,
    ATAQUES_PROTEGIDOS, DURACION_ORBITA, RADIO_ORBITA,
    VELOCIDAD_ANGULAR_ORBITA,
)
from clases.rutas import resolver


class Orbita:
    """Super poder 2: satélite que orbita al repartidor y lo salva de 3 ataques.

    Cada enemigo que llega al repartidor mientras la órbita está activa es
    consumido por el satélite en lugar de golpearlo, y gasta una protección.
    """

    ANCHO = 36
    ALTO = 36

    def __init__(self):
        self.imagen = pygame.transform.scale(
            pygame.image.load(resolver("assets/imagenes/super_poder_2.png")),
            (self.ANCHO, self.ALTO),
        )
        self.angulo = 0.0
        self.x = 0
        self.y = 0
        self.protecciones = ATAQUES_PROTEGIDOS
        self.tiempo_inicio = pygame.time.get_ticks()

    def actualizar(self, centro_x, centro_y):
        self.angulo += VELOCIDAD_ANGULAR_ORBITA
        self.x = centro_x + RADIO_ORBITA * math.cos(self.angulo)
        self.y = centro_y + RADIO_ORBITA * math.sin(self.angulo)

    def ha_expirado(self, tiempo_actual):
        return tiempo_actual - self.tiempo_inicio >= DURACION_ORBITA

    def esta_fuera_de_pantalla(self):
        return (self.x < -self.ANCHO or self.x > ANCHO_PANTALLA or
                self.y < -self.ALTO or self.y > ALTO_PANTALLA)

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, (self.x, self.y))
