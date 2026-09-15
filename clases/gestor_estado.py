import pygame
from clases.config import (
    VIDAS_INICIALES, DURACION_INVULNERABILIDAD,
    ESTADO_JUGANDO, ESTADO_TERMINADO,
)


class GestorEstado:
    def __init__(self):
        self.vidas = VIDAS_INICIALES
        self.puntaje = 0
        self.estado = ESTADO_JUGANDO
        self.tiempo_inicio = pygame.time.get_ticks()
        self.tiempo_fin = 0
        self.invulnerable = False
        self.tiempo_invulnerable = 0
        self.duracion_invulnerabilidad = DURACION_INVULNERABILIDAD

    def perder_vida(self):
        if self.invulnerable:
            return False
        self.vidas -= 1
        self.invulnerable = True
        self.tiempo_invulnerable = pygame.time.get_ticks()
        if self.vidas <= 0:
            self.estado = ESTADO_TERMINADO
            self.tiempo_fin = pygame.time.get_ticks()
        return True

    def sumar_puntaje(self, puntos=1):
        self.puntaje += puntos

    def actualizar_invencibilidad(self, tiempo_actual):
        if self.invulnerable and tiempo_actual - self.tiempo_invulnerable >= self.duracion_invulnerabilidad:
            self.invulnerable = False

    def esta_invulnerable(self):
        return self.invulnerable

    def obtener_tiempo_transcurrido(self, tiempo_actual):
        if self.estado == ESTADO_JUGANDO:
            return tiempo_actual - self.tiempo_inicio
        return self.tiempo_fin - self.tiempo_inicio

    def juego_terminado(self):
        return self.estado == ESTADO_TERMINADO

    def reiniciar(self):
        self.vidas = VIDAS_INICIALES
        self.puntaje = 0
        self.estado = ESTADO_JUGANDO
        self.tiempo_inicio = pygame.time.get_ticks()
        self.tiempo_fin = 0
        self.invulnerable = False
        self.tiempo_invulnerable = 0
