from .enemigo import Enemigo


class Perro(Enemigo):
    ancho = 54
    alto = 64
    velocidad = 0.5

    def __init__(self):
        super().__init__()
        self.cargar_imagen("assets/imagenes/perro.png")
