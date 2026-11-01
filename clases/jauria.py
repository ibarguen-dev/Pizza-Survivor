import math
import random

from clases.config import (
    ALTO_JAURIA, ANCHO_JAURIA, RADIO_COLISION_JAURIA, VELOCIDAD_JAURIA,
)
from clases.enemigo import Enemigo


class Jauria(Enemigo):
    """Perro invocado por el jefe perro zombi.

    A diferencia de los enemigos comunes, estos perros no persiguen al
    repartidor: salen de un borde y avanzan en línea recta hasta salir de
    la pantalla.
    """

    ancho = ANCHO_JAURIA
    alto = ALTO_JAURIA
    velocidad = VELOCIDAD_JAURIA
    radio_colision = RADIO_COLISION_JAURIA
    es_jauria = True

    def __init__(self, objetivo_x=None, objetivo_y=None):
        super().__init__()
        self.cargar_imagen("assets/imagenes/perro.png")
        # Dirección fija en el momento de aparecer: nunca corrige hacia el repartidor.
        if objetivo_x is None:
            angulo = random.uniform(0, math.tau)
            dx, dy = math.cos(angulo), math.sin(angulo)
        else:
            cx, cy = self.obtener_centro()
            dx, dy = objetivo_x - cx, objetivo_y - cy
            distancia = math.hypot(dx, dy)
            if distancia == 0:
                dx, dy = 1, 0
            else:
                dx, dy = dx / distancia, dy / distancia
        self.dx = dx * self.velocidad
        self.dy = dy * self.velocidad

    def actualizar_movimiento(self, objetivo_x, objetivo_y):
        """La jauría avanza en línea recta: ignora por completo al repartidor."""
        self.x += self.dx
        self.y += self.dy
