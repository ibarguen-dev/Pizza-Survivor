from clases.config import (
    ANCHO_PROYECTIL_JEFE, ALTO_PROYECTIL_JEFE,
    RADIO_COLISION_PROYECTIL_JEFE, VELOCIDAD_PROYECTIL_JEFE,
)
from clases.proyectil import Proyectil
from clases.recursos import cargar_imagen


class ProyectilJefe(Proyectil):
    """Proyectil que disparan los jefes para golpear al repartidor."""

    ancho = ANCHO_PROYECTIL_JEFE
    alto = ALTO_PROYECTIL_JEFE
    velocidad = VELOCIDAD_PROYECTIL_JEFE
    radio_colision = RADIO_COLISION_PROYECTIL_JEFE

    def __init__(self, x, y, objetivo_x, objetivo_y):
        super().__init__(x, y, objetivo_x, objetivo_y)
        self.imagen = cargar_imagen(
            "assets/imagenes/proyectil_jefe.png", self.ancho, self.alto
        )

    def colisiona_con_repartidor(self, repartidor):
        cx, cy = self.obtener_centro()
        px, py = repartidor.obtener_centro()
        dx = cx - px
        dy = cy - py
        return (dx ** 2 + dy ** 2) ** 0.5 < self.radio_colision
