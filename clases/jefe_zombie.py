import pygame

from clases.config import (
    ALTO_JEFE, ANCHO_JEFE, DURACION_DESCANSO_ZOMBIE, DURACION_IRA_ZOMBIE,
    VELOCIDAD_DESCANSO_ZOMBIE, VELOCIDAD_IRA_ZOMBIE,
)
from clases.jefe import Jefe
from clases.recursos import cargar_imagen_jefe


class JefeZombie(Jefe):
    """Jefe zombie humano.

    Se specialize en la ira: persigue al repartidor durante
    DURACION_IRA_ZOMBIE y después descansa DURACION_DESCANSO_ZOMBIE, momento
    en el que apenas se mueve.
    """

    nombre = "Zombie"

    def __init__(self):
        super().__init__()
        self.imagen = cargar_imagen_jefe(
            "assets/imagenes/zombie.png", ANCHO_JEFE, ALTO_JEFE,
            color=(104, 156, 92),
        )
        self.en_ira = True
        self.tiempo_estado = pygame.time.get_ticks()
        self.velocidad = VELOCIDAD_IRA_ZOMBIE

    def actualizar_movimiento(self, objetivo_x, objetivo_y):
        """Alterna entre la ira (persecución) y el descanso."""
        ahora = pygame.time.get_ticks()
        if self.en_ira:
            if ahora - self.tiempo_estado >= DURACION_IRA_ZOMBIE:
                self.en_ira = False
                self.tiempo_estado = ahora
                self.velocidad = VELOCIDAD_DESCANSO_ZOMBIE
        elif ahora - self.tiempo_estado >= DURACION_DESCANSO_ZOMBIE:
            self.en_ira = True
            self.tiempo_estado = ahora
            self.velocidad = VELOCIDAD_IRA_ZOMBIE
        self.mover_hacia(objetivo_x, objetivo_y)

    def esta_en_ira(self):
        return self.en_ira
