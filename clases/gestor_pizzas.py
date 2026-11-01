import pygame

from clases.config import (
    ANCHO_PANTALLA, ALTO_PANTALLA,
    INTERVALO_RECARGA_PIZZA, PIZZAS_MANUALES_MAXIMAS,
    PUNTOS_POR_GOLPE_JEFE,
)
from clases.pizza_manual import PizzaManual
from clases.recursos import cargar_imagen


class GestorPizzas:
    """Munición de pizzas manuales (tecla E).

    El repartidor puede llevar 5 pizzas. Cuando se le agotan recupera una
    cada INTERVALO_RECARGA_PIZZA (3,5 segundos). Las pizzas solo se lanzan
    contra los jefes: si no hay ningún jefe en pantalla, la tecla E no
    hace nada y no se gasta munición.
    """

    TAMANO_ICONO = 26

    def __init__(self):
        self.disponibles = PIZZAS_MANUALES_MAXIMAS
        self.ultima_recarga = pygame.time.get_ticks()
        self.pizzas = []
        self.icono = cargar_imagen(
            "assets/imagenes/pizza.png", self.TAMANO_ICONO, self.TAMANO_ICONO
        )
        self.fuente = pygame.font.Font(None, 26)

    # ------------------------------------------------------------------ #
    # Lanzamiento
    # ------------------------------------------------------------------ #
    def lanzar(self, repartidor, gestor_jefes):
        """Lanza una pizza al jefe más cercano. Devuelve True si se lanzó."""
        if self.disponibles <= 0:
            return False
        cx, cy = repartidor.obtener_centro()
        jefe = gestor_jefes.jefe_mas_cercano(cx, cy)
        if jefe is None:
            # Sin jefe no hay pizza que lanzar y no se gasta munición.
            return False
        ox, oy = jefe.obtener_centro()
        self.pizzas.append(PizzaManual(cx - 16, cy - 16, ox, oy))
        self.disponibles -= 1
        # La recarga empieza a contar desde el último lanzamiento.
        self.ultima_recarga = pygame.time.get_ticks()
        return True

    # ------------------------------------------------------------------ #
    # Bucle principal
    # ------------------------------------------------------------------ #
    def actualizar(self, tiempo_actual, gestor_enemigos):
        """Recarga munición y mueve las pizzas. Devuelve los puntos obtenus."""
        self._recargar(tiempo_actual)
        puntos = 0
        for pizza in list(self.pizzas):
            pizza.mover()
            enemigo = self._enemigo_tocado(pizza, gestor_enemigos)
            if enemigo is not None:
                if enemigo.es_jefe:
                    # Un impacto: hacen falta 3 para quitarle una vida.
                    if not enemigo.recibir_dano(1):
                        puntos += PUNTOS_POR_GOLPE_JEFE
                # Si es un enemigo común la pizza se pierde sin dañarlo.
                self.pizzas.remove(pizza)
            elif pizza.esta_fuera_de_pantalla(ANCHO_PANTALLA, ALTO_PANTALLA):
                self.pizzas.remove(pizza)
        return puntos

    def _recargar(self, tiempo_actual):
        if self.disponibles >= PIZZAS_MANUALES_MAXIMAS:
            return
        if tiempo_actual - self.ultima_recarga < INTERVALO_RECARGA_PIZZA:
            return
        self.disponibles += 1
        self.ultima_recarga = tiempo_actual

    def _enemigo_tocado(self, pizza, gestor_enemigos):
        """Primer enemigo que toca la pizza (el más cercano)."""
        enemigo = None
        menor_distancia = float('inf')
        px, py = pizza.obtener_centro()
        for candidato in gestor_enemigos.enemigos:
            if not pizza.colisiona_con(candidato):
                continue
            cx, cy = candidato.obtener_centro()
            distancia = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
            if distancia < menor_distancia:
                menor_distancia = distancia
                enemigo = candidato
        return enemigo

    # ------------------------------------------------------------------ #
    # Dibujo
    # ------------------------------------------------------------------ #
    def dibujar(self, pantalla):
        for pizza in self.pizzas:
            pizza.dibujar(pantalla)

    def dibujar_municion(self, pantalla, x=10, y=566):
        """Muestra las pizzas disponibles en la parte inferior izquierda."""
        for i in range(PIZZAS_MANUALES_MAXIMAS):
            icono = self.icono
            if i >= self.disponibles:
                icono = self.icono.copy()
                icono.set_alpha(70)
            pantalla.blit(icono, (x + i * 30, y))
        etiqueta = self.fuente.render(f"x{self.disponibles}", True, (255, 255, 255))
        pantalla.blit(etiqueta, (x + PIZZAS_MANUALES_MAXIMAS * 30 + 4, y + 2))
