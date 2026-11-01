import pygame

from clases.config import (
    ALTO_JEFE, ANCHO_JEFE, CANTIDAD_JAURIA, INTERVALO_INVOCACION_JEFE,
)
from clases.jauria import Jauria
from clases.jefe import Jefe
from clases.recursos import cargar_imagen_jefe


class JefePerro(Jefe):
    """Jefe perro zombi.

    Se mueve lentamente hacia el repartidor y cada INTERVALO_INVOCACION_JEFE
    invoca una jauría de perros que aparecen en cualquiera de los cuatro
    bordes de la pantalla.
    """

    nombre = "Perro Zombi"

    def __init__(self):
        super().__init__()
        self.imagen = cargar_imagen_jefe(
            "assets/imagenes/perro_zombie.png", ANCHO_JEFE, ALTO_JEFE,
            color=(146, 108, 66),
        )
        self.tiempo_invocacion = pygame.time.get_ticks()

    def actualizar_comportamiento(self, tiempo_actual, repartidor, gestor_enemigos):
        super().actualizar_comportamiento(tiempo_actual, repartidor, gestor_enemigos)
        if tiempo_actual - self.tiempo_invocacion < INTERVALO_INVOCACION_JEFE:
            return
        self.tiempo_invocacion = tiempo_actual
        self.invocar_jauria(repartidor, gestor_enemigos)

    def invocar_jauria(self, repartidor, gestor_enemigos):
        """Llama a CANTIDAD_JAURIA perros, cada uno desde un borde al azar."""
        px, py = repartidor.obtener_centro()
        for _ in range(CANTIDAD_JAURIA):
            jauria = Jauria(px, py)
            gestor_enemigos.enemigos.append(jauria)
