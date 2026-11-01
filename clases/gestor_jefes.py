import random

import pygame

from clases.config import (
    ANCHO_PANTALLA, ALTO_PANTALLA,
    IMPACTOS_POR_VIDA_JEFE, INTERVALO_APARICION_JEFE,
    MAX_JEFES_SIMULTANEOS, PUNTOS_JEFE, VIDAS_JEFE,
)
from clases.jefe_perro import JefePerro
from clases.jefe_zombie import JefeZombie
from clases.recursos import imagen_cabeza_jefe


class GestorJefes:
    """Gestiona la aparición de los jefes, sus proyectiles y su barra de vida.

    Un jefe aparece cada INTERVALO_APARICION_JEFE (5 minutos), elegido al
    azar entre el perro zombi y el zombie humano.
    """

    TIPOS_JEFE = (JefePerro, JefeZombie)

    # Las vidas del jefe se muestran con la imagen de la cabeza, igual que el
    # repartidor muestra las suyas con corazones.
    TAMANO_VIDA = 36
    SEPARACION_VIDA = 4
    X_VIDAS = 200
    Y_VIDAS = 56

    def __init__(self, gestor_enemigos):
        self.gestor_enemigos = gestor_enemigos
        self.jefes = []
        self.tiempo_ultimo_jefe = pygame.time.get_ticks()
        # La cabeza del jefe: la del repartidor pero al revés.
        self.cabeza = imagen_cabeza_jefe(self.TAMANO_VIDA, self.TAMANO_VIDA)
        # La misma cabeza, apagada: marca las vidas ya perdidas.
        self.cabeza_apagada = self.cabeza.copy()
        self.cabeza_apagada.fill((60, 60, 70, 190), special_flags=pygame.BLEND_RGBA_MULT)
        self.fuente = pygame.font.Font(None, 24)

    # ------------------------------------------------------------------ #
    # Bucle principal
    # ------------------------------------------------------------------ #
    def actualizar(self, tiempo_actual, repartidor):
        """Actualiza los jefes. Devuelve (puntos, golpe_recibido)."""
        self._gestionar_spawn(tiempo_actual)
        puntos = 0
        golpe_recibido = False
        for jefe in list(self.jefes):
            jefe.actualizar_comportamiento(tiempo_actual, repartidor, self.gestor_enemigos)
            if self._actualizar_proyectiles(jefe, repartidor):
                golpe_recibido = True
            if jefe.esta_muerto():
                puntos += PUNTOS_JEFE
                self._eliminar_jefe(jefe)
        return puntos, golpe_recibido

    def _gestionar_spawn(self, tiempo_actual):
        if tiempo_actual - self.tiempo_ultimo_jefe < INTERVALO_APARICION_JEFE:
            return
        self.tiempo_ultimo_jefe = tiempo_actual
        if len(self.jefes) >= MAX_JEFES_SIMULTANEOS:
            return
        clase = random.choice(self.TIPOS_JEFE)
        jefe = clase()
        self.jefes.append(jefe)
        self.gestor_enemigos.enemigos.append(jefe)

    def _actualizar_proyectiles(self, jefe, repartidor):
        """Mueve los proyectiles del jefe. Devuelve True si golpearon al repartidor."""
        golpe = False
        for proyectil in list(jefe.proyectiles):
            proyectil.mover()
            if proyectil.colisiona_con_repartidor(repartidor):
                golpe = True
                jefe.proyectiles.remove(proyectil)
            elif proyectil.esta_fuera_de_pantalla(ANCHO_PANTALLA, ALTO_PANTALLA):
                jefe.proyectiles.remove(proyectil)
        return golpe

    def _eliminar_jefe(self, jefe):
        self.jefes.remove(jefe)
        if jefe in self.gestor_enemigos.enemigos:
            self.gestor_enemigos.enemigos.remove(jefe)

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    def hay_jefe(self):
        return len(self.jefes) > 0

    def jefe_mas_cercano(self, objetivo_x, objetivo_y):
        if not self.jefes:
            return None
        return min(
            self.jefes,
            key=lambda jefe: jefe.distancia_hacia(objetivo_x, objetivo_y),
        )

    # ------------------------------------------------------------------ #
    # Dibujo
    # ------------------------------------------------------------------ #
    def dibujar(self, pantalla):
        for jefe in self.jefes:
            for proyectil in jefe.proyectiles:
                proyectil.dibujar(pantalla)

    def dibujar_barras_vida(self, pantalla):
        """Vidas de cada jefe. Solo aparecen si hay un jefe en pantalla."""
        for i, jefe in enumerate(self.jefes):
            y = self.Y_VIDAS + i * (self.TAMANO_VIDA + 18)

            # Nombre del jefe encima de sus vidas.
            etiqueta = self.fuente.render(jefe.nombre, True, (255, 255, 255))
            pantalla.blit(etiqueta, (self.X_VIDAS, y - 20))

            # Una cabeza por cada vida: las que ya perdió se ven apagadas.
            for n in range(VIDAS_JEFE):
                x = self.X_VIDAS + n * (self.TAMANO_VIDA + self.SEPARACION_VIDA)
                icono = self.cabeza if n < jefe.vidas else self.cabeza_apagada
                pantalla.blit(icono, (x, y))

            # Barra de la vida actual: muestra los impactos que le quedan
            # para perderla (3 impactos = 1 vida).
            if jefe.impactos > 0:
                self._dibujar_barra_impactos(pantalla, jefe, y)
            elif jefe.vidas < VIDAS_JEFE:
                # Ya no le queda vida parcial: se avisa con el borde vacío.
                ancho = VIDAS_JEFE * (self.TAMANO_VIDA + self.SEPARACION_VIDA)
                rect = pygame.Rect(self.X_VIDAS, y + self.TAMANO_VIDA + 2, ancho, 5)
                pygame.draw.rect(pantalla, (70, 70, 80), rect)

    def _dibujar_barra_impactos(self, pantalla, jefe, y):
        """Barrita naranja con la parte de vida que le queda al jefe."""
        ancho_total = VIDAS_JEFE * (self.TAMANO_VIDA + self.SEPARACION_VIDA)
        restante = IMPACTOS_POR_VIDA_JEFE - jefe.impactos
        proporcion = max(0, restante) / IMPACTOS_POR_VIDA_JEFE
        alto = 5
        y_barra = y + self.TAMANO_VIDA + 2
        rect = pygame.Rect(self.X_VIDAS, y_barra, ancho_total, alto)
        pygame.draw.rect(pantalla, (70, 70, 80), rect)
        pygame.draw.rect(
            pantalla, (255, 180, 60),
            pygame.Rect(self.X_VIDAS, y_barra, int(ancho_total * proporcion), alto),
        )
