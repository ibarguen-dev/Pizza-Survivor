from .proyectil import Proyectil


class Pizza(Proyectil):
    ancho = 32
    alto = 32
    velocidad = 1.5

    def __init__(self, x, y, objetivo_x, objetivo_y):
        super().__init__(x, y, objetivo_x, objetivo_y)
        self.cargar_imagen("assets/imagenes/pizza.png")
