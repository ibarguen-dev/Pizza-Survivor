import pygame

from clases.config import (
    IMPACTOS_POR_VIDA_JEFE, INTERVALO_ATAQUE_JEFE,
    RADIO_COLISION_JEFE, VELOCIDAD_JEFE, VIDAS_JEFE,
)
from clases.enemigo import Enemigo
from clases.proyectil_jefe import ProyectilJefe


class Jefe(Enemigo):
    """Base de los jefes.

    Un jefe tiene 5 vidas. Cada proyectil que lo golpea cuenta como un
    impacto y hacen falta 3 impactos para quitarle una vida. El super poder
    1 (onda perforante) es la excepción: con un solo toque le quita una
    vida entera, pero el poder desaparece al tocarlo.
    """

    es_jefe = True
    vidas = VIDAS_JEFE
    radio_colision = RADIO_COLISION_JEFE
    velocidad = VELOCIDAD_JEFE
    nombre = "Jefe"

    def __init__(self):
        super().__init__()
        self.vidas = VIDAS_JEFE
        # Impactos acumulados en la vida actual (0 a IMPACTOS_POR_VIDA_JEFE)
        self.impactos = 0
        self.proyectiles = []
        self.tiempo_disparo = pygame.time.get_ticks()

    # ------------------------------------------------------------------ #
    # Daño
    # ------------------------------------------------------------------ #
    def recibir_dano(self, cantidad=1):
        """Suma impactos. Cada IMPACTOS_POR_VIDA_JEFE impactos quitan una vida."""
        for _ in range(cantidad):
            self.impactos += 1
            if self.impactos >= IMPACTOS_POR_VIDA_JEFE:
                self.impactos = 0
                self.vidas -= 1
        return self.esta_muerto()

    def perder_vida_directa(self):
        """El super poder 1 quita una vida de un solo golpe."""
        self.vidas -= 1
        self.impactos = 0
        return self.esta_muerto()

    def esta_muerto(self):
        return self.vidas <= 0

    # ------------------------------------------------------------------ #
    # Comportamiento
    # ------------------------------------------------------------------ #
    def actualizar_comportamiento(self, tiempo_actual, repartidor, gestor_enemigos):
        """Se llama una vez por frame para el comportamiento propio de cada jefe."""
        self.intentar_disparar(tiempo_actual, repartidor)

    def intentar_disparar(self, tiempo_actual, repartidor):
        """Dispara un proyectil al repartidor cada INTERVALO_ATAQUE_JEFE."""
        if tiempo_actual - self.tiempo_disparo < INTERVALO_ATAQUE_JEFE:
            return
        self.tiempo_disparo = tiempo_actual
        cx, cy = self.obtener_centro()
        px, py = repartidor.obtener_centro()
        self.proyectiles.append(ProyectilJefe(cx, cy, px, py))
