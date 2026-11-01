"""Partida en curso: orquesta todos los sistemas del juego.

Cada vez que se empieza una partida se crea un objeto `Juego` nuevo, así que
reiniciar tras un game over es simplemente crear otro (sin residuos de la
partida anterior).
"""
import pygame

from clases.config import (
    INTERVALO_LANZAMIENTO, INTERVALO_SPAWN_GATO, INTERVALO_SPAWN_PERRO,
    PUNTOS_POR_GOLPE, PUNTOS_POR_GOLPE_JEFE,
)
from clases.gato import Gato
from clases.gestor_enemigos import GestorEnemigos
from clases.gestor_estado import GestorEstado
from clases.gestor_jefes import GestorJefes
from clases.gestor_pizzas import GestorPizzas
from clases.gestor_poderes import GestorPoderes
from clases.gestor_proyectiles import GestorProyectiles
from clases.perro import Perro
from clases.pizza import Pizza
from clases.repartidor import Repartidor


class Juego:
    """Una partida completa: repartidor, enemigos, jefes, poderes y proyectiles."""

    def __init__(self, sonidos=None):
        self.sonidos = sonidos or {}

        # Repartidor
        self.repartidor = Repartidor(368, 440, "assets/imagenes/repartidor.png")

        # Enemigos comunes: los perros aparecen más a menudo que los gatos
        self.gestor_enemigos = GestorEnemigos()
        self.gestor_enemigos.agregar_tipo(Perro, INTERVALO_SPAWN_PERRO)
        self.gestor_enemigos.agregar_tipo(
            Gato, intervalo_spawn=INTERVALO_SPAWN_GATO, velocidad=0.7
        )

        # Proyectiles automáticos (pizzas), estado, poderes, jefes y munición
        self.gestor_proyectiles = GestorProyectiles(Pizza)
        self.gestor_estado = GestorEstado()
        self.gestor_poderes = GestorPoderes(self.gestor_estado)
        self.gestor_jefes = GestorJefes(self.gestor_enemigos)
        self.gestor_pizzas = GestorPizzas()

        self.tiempo_ultimo_lanzamiento = pygame.time.get_ticks()

    # ------------------------------------------------------------------ #
    # Entrada
    # ------------------------------------------------------------------ #
    def manejar_evento(self, evento):
        """Procesa un evento de teclado. Devuelve "menu" si se pide salir."""
        if evento.type == pygame.QUIT:
            return "salir"

        if evento.type in (pygame.KEYDOWN, pygame.KEYUP):
            presionada = evento.type == pygame.KEYDOWN
            self.repartidor.recibir_evento_tecla(evento.key, presionada)

            # Barra espaciadora: activa el super poder que toca en la cola.
            if presionada and evento.key == pygame.K_SPACE:
                if self.gestor_poderes.usar(self.repartidor, self.gestor_enemigos):
                    self._reproducir("disparo")

            # Tecla E: lanza una pizza manual al jefe más cercano.
            if presionada and evento.key == pygame.K_e:
                if self.gestor_pizzas.lanzar(self.repartidor, self.gestor_jefes):
                    self._reproducir("disparo")

            # ESC: vuelve al menú principal.
            if presionada and evento.key == pygame.K_ESCAPE:
                return "menu"

        return None

    def _reproducir(self, nombre):
        sonido = self.sonidos.get(nombre)
        if sonido is not None:
            sonido.play()

    # ------------------------------------------------------------------ #
    # Lógica
    # ------------------------------------------------------------------ #
    def actualizar(self, tiempo_actual):
        """Avanza la simulación un frame. Devuelve True si la partida terminó."""
        self.repartidor.mover()

        rx, ry = self.repartidor.obtener_posicion()
        self.gestor_enemigos.actualizar(tiempo_actual, rx + 32, ry + 50)
        self.gestor_enemigos.limpiar()
        self.gestor_enemigos.aumentar_dificultad(tiempo_actual)

        # Jefes: aparecen, se mueven con su comportamiento y disparan proyectiles.
        puntos_jefes, golpe_jefe = self.gestor_jefes.actualizar(
            tiempo_actual, self.repartidor
        )
        if puntos_jefes > 0:
            self.gestor_estado.sumar_puntaje(puntos_jefes)
        if golpe_jefe:
            self.aplicar_golpe()

        # Lanzamiento automático de pizzas al enemigo más cercano.
        if tiempo_actual - self.tiempo_ultimo_lanzamiento >= INTERVALO_LANZAMIENTO:
            objetivo = self.gestor_enemigos.encontrar_mas_cercano(rx + 32, ry + 50)
            if objetivo:
                ox, oy = objetivo.obtener_centro()
                self.gestor_proyectiles.lanzar(rx + 32, ry + 50, ox, oy)
                self._reproducir("disparo")
            self.tiempo_ultimo_lanzamiento = tiempo_actual

        self.gestor_proyectiles.actualizar()
        golpeados = self.gestor_proyectiles.detectar_colisiones_enemigos(
            self.gestor_enemigos
        )
        if golpeados:
            puntos = sum(
                PUNTOS_POR_GOLPE_JEFE if enemigo.es_jefe else PUNTOS_POR_GOLPE
                for enemigo in golpeados
            )
            self.gestor_estado.sumar_puntaje(puntos)
            self._reproducir("golpe")

        # Pizzas manuales (tecla E): solo van a por los jefes.
        puntos_pizzas = self.gestor_pizzas.actualizar(tiempo_actual, self.gestor_enemigos)
        if puntos_pizzas > 0:
            self.gestor_estado.sumar_puntaje(puntos_pizzas)
            self._reproducir("golpe")

        # Puntos y recogibles de super poderes / vidas extra.
        puntos_poderes = self.gestor_poderes.actualizar(
            tiempo_actual, self.repartidor, self.gestor_enemigos
        )
        if puntos_poderes > 0:
            self.gestor_estado.sumar_puntaje(puntos_poderes)
            self._reproducir("golpe")

        # La órbita absorbe los golpes de los enemigos (hasta 3 ataques).
        if self.gestor_enemigos.detectar_colision_repartidor(self.repartidor) > 0:
            self.aplicar_golpe()

        self.gestor_estado.actualizar_invencibilidad(tiempo_actual)
        return self.gestor_estado.juego_terminado()

    def aplicar_golpe(self):
        """El repartidor recibe un golpe: pierde una vida si no está protegido."""
        if self.gestor_estado.esta_invulnerable():
            return
        if self.gestor_poderes.proteger_ataque():
            # La órbita salvó al repartidor: el enemigo ya fue consumido.
            return
        if self.gestor_estado.perder_vida():
            self._reproducir("vida_perdida")

    # ------------------------------------------------------------------ #
    # Dibujo
    # ------------------------------------------------------------------ #
    def dibujar(self, pantalla, fondo, fuentes, corazon_img):
        """Dibuja la escena completa de la partida."""
        pantalla.blit(fondo, (0, 0))
        self._dibujar_vidas(pantalla, corazon_img)
        self.gestor_poderes.dibujar_inventario(pantalla)
        self._dibujar_puntaje(pantalla, fuentes["normal"])
        self._dibujar_cronometro(pantalla, fuentes["normal"])

        # El repartidor parpadea mientras es invulnerable.
        tiempo_actual = pygame.time.get_ticks()
        if (not self.gestor_estado.esta_invulnerable()
                or (tiempo_actual // 100) % 2 == 0):
            self.repartidor.dibujar(pantalla)

        self.gestor_enemigos.dibujar(pantalla)
        self.gestor_proyectiles.dibujar(pantalla)
        self.gestor_pizzas.dibujar(pantalla)
        self.gestor_poderes.dibujar(pantalla)
        self.gestor_jefes.dibujar(pantalla)

        # La barra de vida del jefe solo aparece cuando hay un jefe en pantalla.
        self.gestor_jefes.dibujar_barras_vida(pantalla)
        self.gestor_pizzas.dibujar_municion(pantalla)

    def _dibujar_vidas(self, pantalla, corazon_img):
        for i in range(self.gestor_estado.vidas):
            pantalla.blit(corazon_img, (10 + i * 36, 10))

    def _dibujar_puntaje(self, pantalla, fuente):
        texto = fuente.render(f"puntaje: {self.gestor_estado.puntaje}", True, (255, 255, 255))
        pantalla.blit(texto, (650, 10))

    def _dibujar_cronometro(self, pantalla, fuente):
        tt = self.gestor_estado.obtener_tiempo_transcurrido(pygame.time.get_ticks())
        minutos = tt // 60000
        segundos = (tt % 60000) // 1000
        texto = fuente.render(f"Tiempo: {minutos}:{segundos:02d}", True, (255, 255, 255))
        pantalla.blit(texto, (350, 10))
