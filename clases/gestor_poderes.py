import math
import random

import pygame

from clases.config import (
    ATAQUES_PROTEGIDOS, CARGAS_MAXIMAS_PODER,
    INTERVALO_SPAWN_RECOGIBLE_MAX, INTERVALO_SPAWN_RECOGIBLE_MIN,
    RADIO_RECOGIBLE, TIPO_ORBITA, TIPO_PERFORANTE, TIPO_VIDA,
    VENTANA_VIDA_EXTRA,
)
from clases.orbita import Orbita
from clases.onda_perforante import OndaPerforante
from clases.recogible import Recogible
from clases.rutas import resolver


class Poder:
    """Un super poder del inventario del repartidor, con sus cargas restantes."""

    def __init__(self, tipo, cargas=CARGAS_MAXIMAS_PODER):
        self.tipo = tipo
        self.cargas = cargas

    @property
    def esta_lleno(self):
        return self.cargas >= CARGAS_MAXIMAS_PODER


class GestorPoderes:
    """Gestiona los super poderes y las vidas extra del repartidor.

    Reglas:
    - Los recogibles (poder 1, poder 2 o corazón) aparecen en pantalla y el
      repartidor debe tocarlos para obtenerlos.
    - Cada super poder se puede usar hasta 3 veces (barra espaciadora).
    - Se pueden tener los dos super poderes a la vez, pero solo se gasta el
      primero que se agarró; cuando se agota, pasa a consumirse el segundo.
    - Al agarrar un poder que ya se tiene, solo se restaura lo que falta
      (hasta 3 cargas). Si ya está lleno, se entrega una vida extra.
    """

    ICONO = {
        TIPO_PERFORANTE: "assets/imagenes/super_poder_1.png",
        TIPO_ORBITA: "assets/imagenes/super_poder_2.png",
    }

    def __init__(self, gestor_estado):
        self.gestor_estado = gestor_estado
        self.poderes = []          # cola de poderes: primero en usar va primero
        self.recogibles = []
        self.ondas = []
        self.orbita = None
        self.ultimo_spawn = pygame.time.get_ticks()
        self.intervalo_spawn = self._elegir_intervalo()
        self.iconos = {
            tipo: pygame.transform.scale(pygame.image.load(resolver(ruta)), (32, 32))
            for tipo, ruta in self.ICONO.items()
        }
        self.fuente = pygame.font.Font(None, 24)

    # ------------------------------------------------------------------ #
    # Bucle principal
    # ------------------------------------------------------------------ #
    def actualizar(self, tiempo_actual, repartidor, gestor_enemigos):
        """Actualiza recogibles, ondas y órbita. Devuelve puntos por enemigos."""
        self._gestionar_spawn(tiempo_actual)
        puntos = 0
        puntos += self._actualizar_recogibles(repartidor)
        puntos += self._actualizar_ondas(gestor_enemigos)
        self._actualizar_orbita(tiempo_actual, repartidor)
        return puntos

    def _gestionar_spawn(self, tiempo_actual):
        if tiempo_actual - self.ultimo_spawn < self.intervalo_spawn:
            return
        self.ultimo_spawn = tiempo_actual
        self.intervalo_spawn = self._elegir_intervalo()
        self.recogibles.append(Recogible(self._elegir_tipo(tiempo_actual)))

    def _elegir_intervalo(self):
        return random.randint(INTERVALO_SPAWN_RECOGIBLE_MIN, INTERVALO_SPAWN_RECOGIBLE_MAX)

    def _elegir_tipo(self, tiempo_actual):
        """Durante los primeros 2 minutos también pueden aparecer vidas extra."""
        if tiempo_actual < VENTANA_VIDA_EXTRA:
            return random.choice([TIPO_PERFORANTE, TIPO_ORBITA, TIPO_VIDA])
        return random.choice([TIPO_PERFORANTE, TIPO_ORBITA])

    def _actualizar_recogibles(self, repartidor):
        rx, ry = repartidor.obtener_centro()
        puntos = 0
        for recogible in list(self.recogibles):
            recogible.mover()
            if recogible.colisiona_con(rx, ry, RADIO_RECOGIBLE):
                self.recogibles.remove(recogible)
                self._recolectar(recogible)
                puntos += 1
            elif recogible.esta_expirado(pygame.time.get_ticks()):
                self.recogibles.remove(recogible)
        return puntos

    def _actualizar_ondas(self, gestor_enemigos):
        puntos = 0
        for onda in list(self.ondas):
            onda.mover()
            puntos += onda.eliminar_enemigos(gestor_enemigos)
            # La onda desaparece si tocó a un jefe o si salió de la pantalla.
            if onda.consumida or onda.esta_fuera_de_pantalla():
                self.ondas.remove(onda)
        return puntos

    def _actualizar_orbita(self, tiempo_actual, repartidor):
        if self.orbita is None:
            return
        if self.orbita.ha_expirado(tiempo_actual):
            self.orbita = None
            return
        cx, cy = repartidor.obtener_centro()
        self.orbita.actualizar(cx, cy)

    # ------------------------------------------------------------------ #
    # Recogida
    # ------------------------------------------------------------------ #
    def _recolectar(self, recogible):
        if recogible.tipo == TIPO_VIDA:
            self.gestor_estado.ganar_vida()
            return

        poder = self._buscar_poder(recogible.tipo)
        if poder is None:
            # Poder nuevo: entra en la cola con todas sus cargas.
            self.poderes.append(Poder(recogible.tipo))
            return

        if poder.esta_lleno:
            # Ya tiene las 3 cargas: se le entrega una vida extra.
            self.gestor_estado.ganar_vida()
            return

        # Solo se restaura lo que le falta.
        poder.cargas = CARGAS_MAXIMAS_PODER

    def _buscar_poder(self, tipo):
        for poder in self.poderes:
            if poder.tipo == tipo:
                return poder
        return None

    # ------------------------------------------------------------------ #
    # Activación con la barra espaciadora
    # ------------------------------------------------------------------ #
    def usar(self, repartidor, gestor_enemigos):
        """Consume una carga del primer poder de la cola y activa su efecto."""
        if not self.poderes:
            return False

        poder = self.poderes[0]
        poder.cargas -= 1
        if poder.cargas <= 0:
            self.poderes.pop(0)

        if poder.tipo == TIPO_PERFORANTE:
            self._activar_perforante(repartidor, gestor_enemigos)
        elif poder.tipo == TIPO_ORBITA:
            self._activar_orbita(repartidor)
        return True

    def _activar_perforante(self, repartidor, gestor_enemigos):
        dx, dy = self._direccion_disparo(repartidor, gestor_enemigos)
        cx, cy = repartidor.obtener_centro()
        self.ondas.append(OndaPerforante(cx - 22, cy - 24, dx, dy))

    def _activar_orbita(self, repartidor):
        # Cada uso del poder deja una órbita nueva con sus 3 protecciones.
        self.orbita = Orbita()
        cx, cy = repartidor.obtener_centro()
        self.orbita.actualizar(cx, cy)

    def _direccion_disparo(self, repartidor, gestor_enemigos):
        cx, cy = repartidor.obtener_centro()
        objetivo = gestor_enemigos.encontrar_mas_cercano(cx, cy)
        if objetivo is not None:
            ox, oy = objetivo.obtener_centro()
            dx, dy = ox - cx, oy - cy
            distancia = math.hypot(dx, dy)
            if distancia > 0:
                return dx / distancia, dy / distancia
        if repartidor.cambio_x or repartidor.cambio_y:
            return repartidor.cambio_x, repartidor.cambio_y
        return 0, -1

    # ------------------------------------------------------------------ #
    # Protección de la órbita
    # ------------------------------------------------------------------ #
    def proteger_ataque(self):
        """La órbita absorbe el golpe. Devuelve True si protegió al repartidor."""
        if self.orbita is None or self.orbita.protecciones <= 0:
            return False
        self.orbita.protecciones -= 1
        if self.orbita.protecciones <= 0:
            self.orbita = None
        return True

    # ------------------------------------------------------------------ #
    # Dibujo
    # ------------------------------------------------------------------ #
    def dibujar(self, pantalla):
        for recogible in self.recogibles:
            recogible.dibujar(pantalla)
        for onda in self.ondas:
            onda.dibujar(pantalla)
        if self.orbita is not None:
            self.orbita.dibujar(pantalla)

    def dibujar_inventario(self, pantalla, x=10, y=48):
        """Muestra los super poderes debajo de las barras de vidas."""
        for i, poder in enumerate(self.poderes):
            pos_x = x + i * 46
            pantalla.blit(self.iconos[poder.tipo], (pos_x, y))
            etiqueta = f"x{poder.cargas}"
            sombra = self.fuente.render(etiqueta, True, (0, 0, 0))
            texto = self.fuente.render(etiqueta, True, (255, 255, 0))
            pantalla.blit(sombra, (pos_x + 21, y + 15))
            pantalla.blit(texto, (pos_x + 20, y + 14))
