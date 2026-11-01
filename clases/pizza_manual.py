from clases.config import VELOCIDAD_PIZZA_MANUAL
from clases.pizza import Pizza


class PizzaManual(Pizza):
    """Pizza que lanza el repartidor a mano con la tecla E.

    Solo se lanzan contra los jefes. Si un enemigo común la toca, la pizza
    se pierde sin dañarlo.
    """

    velocidad = VELOCIDAD_PIZZA_MANUAL
